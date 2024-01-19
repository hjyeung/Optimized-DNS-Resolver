import socket
import struct
import time

def create_query():
    # initialize header variables
    transaction_id = 0x178e # random transaction ID
    flags = 0x0100 # standard query operation
    questions = 0x0001 # one entry in query
    answer_count = 0x0000 # expected responses
    authority_records = 0x0000 # zero number of entries
    additional_records = 0x0000 # zero number of entries

    # initialize query variables
    domain = 'tmz.com'
    encoded_domain = query = b'\x03tmz\x03com\x00'
    query_type = 0x0001 # type A DNS record
    query_class = 0x0001 # class IN query
    
    # create header and query
    header = struct.pack('!HHHHHH', transaction_id, flags, questions, answer_count, authority_records, additional_records)
    query += struct.pack('!HH', query_type, query_class)

    return header + query

def send_query(query, server_array, dns_level):
    def get_record_type(query_response):
        record_type = (" ".join(map(str, struct.unpack('BB', query_response[23:25]))))

        if record_type == '0 1':
            print("DNS type found: A record")
        elif record_type == '0 28':
            print("DNS type found: AAAA record")
        elif record_type == '0 2':
            print("DNS type found: NS record")
        elif record_type == '0 5':
            print("DNS type found: CNAME record")
        
        return 0

    for i in server_array:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket: # create socket object
            client_socket.settimeout(10)  # set timeout of 10 seconds
            initial_time = time.time() # calculation for RTT

            try:
                client_socket.sendto(query, (i, 53)) # send query to DNS under standard port 53
                query_response, _ = client_socket.recvfrom(1024)
                server_array = []

                if dns_level == 0:
                    print("Root Server:", i)
                    get_record_type(query_response)

                final_time = time.time()
                round_trip_time = final_time - initial_time
                print("Round-trip time =", round_trip_time, "seconds\n")
                
                if dns_level == 0:
                    found_address = ".".join(map(str, struct.unpack('BBBB', query_response[261:265])))
                    print("TLD Server:", found_address)
                    get_record_type(query_response)
                    server_array.append(found_address)
                    found_address = send_query(query, server_array, 1)
                    break
                elif dns_level == 1:
                    found_address = ".".join(map(str, struct.unpack('BBBB', query_response[-4:])))
                    print("Authoritative Server:", found_address)
                    get_record_type(query_response)
                    server_array.append(found_address)
                    found_address = send_query(query, server_array, 2)
                    break
                elif dns_level == 2:
                    found_address = ".".join(map(str, struct.unpack('BBBB', query_response[69:73])))
                    print("Final IP address:", found_address)
                    break
            except:
                continue # next iteration in server_array

    return found_address

def send_request(address):
    print("Currently sending HTTP request to", address + "...\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        initial_time = time.time() # calculation for RTT
        request = "GET / HTTP/1.0\r\nHost: " + address + "\r\n\r\n"
        client_socket.connect((address, 80))
        client_socket.sendall(request.encode())
        data = client_socket.recv(1024)

        print(data.decode())
    
    final_time = time.time()
    round_trip_time = final_time - initial_time
    print("\nRound-trip time =", round_trip_time, "seconds\n")

    return data

# main function
server_array = ["198.41.0.4", "199.9.14.201", "192.33.4.12", "199.7.91.13", "192.203.230.10", "192.5.5.241", "192.112.36.4", "198.97.190.53", "192.36.148.17", "192.58.128.30", "193.0.14.129", "199.7.83.42", "202.12.27.33"]

query = create_query()
response = send_query(query, server_array, 0)
request = send_request(response)
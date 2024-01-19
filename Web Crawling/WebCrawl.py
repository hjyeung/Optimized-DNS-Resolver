from browsermobproxy import Server
from selenium import webdriver
import json
import os
import csv
import sys

def create_new_server():
    # create a browsermob server instance
    server = Server(os.getcwd() + r"\browsermob-proxy\bin\browsermob-proxy.bat",
                    options={'port':portname})
    server.start()
    return server

def get_chrome_options(proxy):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-proxy-certificate-handler")
    chrome_options.add_argument("--disable-content-security-policy")
    chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
    return chrome_options

def scraper(url):
    server = create_new_server()
    proxy = server.create_proxy(params=dict(trustAllServers=True))
    driver = webdriver.Chrome(options=get_chrome_options(proxy))

    # do crawling
    proxy = load_web_page(driver, proxy, url)

    # write har file
    add_to_myhar(proxy)

    # stop server and exit
    server.stop()
    driver.quit()

def load_web_page(driver, proxy, url):
    proxy.new_har("myhar")
    try:
        driver.get(url)
    except:
        print("------WE HAD AN ERROR------")
        pass
    return proxy

def add_to_myhar(proxy):
    with open('myhar' + start.__str__() + '-' + end.__str__() + '.har', 'a') as f:
        f.write('\n')
        f.write(json.dumps(proxy.har))

def extract_csv(location):
    with open(location, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        return data
    
def get_list_from_csv(csv, start, end):
    urls = []
    for i in range(start-1, end):
        urls.append("http://" + csv[i][1])
    return urls

if len(sys.argv) < 2:
    print("Usage is: python WebCrawl.py [Port Number] [Starting index from list of websites] [Ending index from list of websites]")
    print("We will default to starting at 1, ending at 1000 on port 8080")
    start = 1
    end = 1000
    portname = 8080
else:
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    portname = int(sys.argv[1])

url_links = get_list_from_csv(extract_csv('top-1m.csv'), 
                              start, end)

for i in range(len(url_links)):
    scraper(url_links[i])
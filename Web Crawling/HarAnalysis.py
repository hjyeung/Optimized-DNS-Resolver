import json
import csv

import collections
from tld import get_fld

cookies = collections.Counter()
def analyze_har():
    urls = collections.Counter()

    with open('myhar.har', 'r') as f:
        all_pages = f.readlines()
    
    iter = 1
    for page in all_pages:        
        urls = log_third_level_domains_and_cookies(urls, page, iter)
        iter += 1 

    print(str(urls.most_common(10)))
    print(str(cookies.most_common(10)))

def log_third_level_domains_and_cookies(urls, page, iter):
    try:
        har_data = json.loads(page)
    except:
        return urls
    firstLevelDomain = get_third_level_domain(har_data['log']['entries'][0]['request']['url'])
    totalthirdLevels = 0

    for item in har_data['log']['entries']:
        url = get_third_level_domain(item['request']['url'])
        log_cookies(item)
        if url != firstLevelDomain and url != "error":
            urls.update([url])
            totalthirdLevels += 1

    #print_line_for_latex(totalthirdLevels, iter)
    return urls

def log_cookies(har):
    if (har['request']['cookies'] != []):
        for cookie in har['request']['cookies']:
            cookies.update([cookie['name']])


def get_third_level_domain(url):
    try:
        output = get_fld(url)
    except:
        output = "error"
    return output

def extract_csv(location):
    with open(location, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        return data

listOfLinks = extract_csv('top-1m.csv')
def print_line_for_latex(totalthirdLevels, iter):
    if (iter % 3) == 0:
        print(listOfLinks[iter-1][1].__str__() + " & " + totalthirdLevels.__str__() + " \\\\\hline")
    else:
        print(listOfLinks[iter-1][1].__str__() + " & " + totalthirdLevels.__str__() + " & ", end="")

analyze_har()
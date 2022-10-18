from cgitb import html
from reprlib import recursive_repr
from sqlite3 import Timestamp
from unittest import result
from bs4 import BeautifulSoup
import requests
import regex
import pandas as pd
import csv


def extract_query_id():
    cookies = None

    # get session
    jsession_id = None
    ret = requests.get('https://shigen.nig.ac.jp/rice/oryzabase/locale/change?lang=en')
    for k, v in ret.cookies.items():
        cookies = {k:v}
        jsession_id = v

    # get timestamp
    ret = requests.get('https://shigen.nig.ac.jp/rice/oryzabase/gene/advanced/list', cookies=cookies)
    soup = BeautifulSoup(ret.text, 'html.parser')
    ancho = soup.find_all("a", {"href": regex.compile(".*page=2")})[0]
    timestamp = ancho['href'].split('&')[-2].split('=')[1]

    return (timestamp, jsession_id)


def crawl(jsession_id, timestamp):
    SessionID = jsession_id
    headers = {'Cookie': 'JSESSIONID=' + (SessionID)}
    Time = timestamp
    ret = requests.post('https://shigen.nig.ac.jp/rice/oryzabase/gene/advanced/pageSort?listName=GENE_SOLR_LIST&timeStamp=' + (Time) + '&page=-1', headers=headers)
    html_text = ret.text
    soup = BeautifulSoup(html_text, 'lxml')
    table = soup.find_all("table", {"class":"table_summery_list table_nowrapTh max_width_element"})[-1]
    rows = table.findAll('tr')
    headers = rows[0]
    header_text = []
    for th in headers.findAll('th'):
        header_text.append(th.text.strip())
    row_text_array = []
    for row in rows[1:]:
        row_text = []
        for row_element in row.findAll(['th', 'td']):
            row_text.append(row_element.text.replace('\n', '').replace('\t', '').replace('\r', '').strip())
        row_text_array.append(row_text)

    with open("out1.csv", "w", encoding="utf-8", newline='') as f:
        wr = csv.writer(f)
        wr.writerow(header_text)
        for row_text_single in row_text_array:
            wr.writerow(row_text_single)


if __name__ == "__main__":
    timestamp, jsession_id = extract_query_id()
    print(f'Detected: timestamp({timestamp}), jsession_id({jsession_id})')
    crawl(jsession_id, timestamp)
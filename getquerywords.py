# -*- coding:utf8 -*-
import requests
import json
import urllib
from urllib import parse
import os
import time
from fake_useragent import UserAgent
from hashlib import md5
import argparse
import shutil
import base64
from bs4 import BeautifulSoup

ua=UserAgent()
header = {'User-Agent':ua.random}
query_words = {
    "all": [],
    "影视安利": [],
    "萌宠萌物": [],
    "劲爆体育": [],
}
hotword_url = "https://www.soogif.com/hotword"
strhtml = requests.get(hotword_url, headers=header, timeout=3)  # Get方式获取网页数据
# with open("./strhtml.json",'w') as f:
#     print(strhtml.text, file=f)
jsonInfo = json.loads(strhtml.text)
for index in range(len(jsonInfo["data"]["list"])):
    query_words["all"].append(jsonInfo['data']["list"][index]['query'])
# print(query_words)



header = {'User-Agent':ua.random}
start_url = "https://www.soogif.com/sort/124"
page = urllib.request.Request(start_url,headers=header)
html = urllib.request.urlopen(page,timeout=3)
soup = BeautifulSoup(html, "lxml")
# with open("./html.html",'w') as f:
#     print(soup.prettify(), file=f)

class_list = soup.html.body.find("div",class_="classification-container").find("ul",class_="classification-list").find_all("li")
# print(class_list)

href_list = []
for gifclass in class_list[:-1]:
    ele = gifclass.find("a",class_="column-link")
    if ele:
        href_list.append({
            "title": ele.attrs["title"],
            "href": "https://www.soogif.com"+ele.attrs["href"]
            })
# print(href_list)



for item in href_list:
    header = {'User-Agent':ua.random}
    now_page = urllib.request.Request(item["href"],headers=header)
    now_html = urllib.request.urlopen(now_page,timeout=3)
    now_soup = BeautifulSoup(now_html, "lxml")
    # with open("./html.html",'w') as f:
        # print(soup.prettify(), file=f)

    title_list = now_soup.html.body.find("div",class_="classification-container").find("div",class_="column-content-list").find_all("a",class_="column-item")
    # print(title_list)
    for title in title_list:
        query_words["all"].append(title.attrs["href"][8:])
        if (item["title"] in query_words.keys()):
            query_words[item["title"]].append(title.attrs["href"][8:])


# print(query_words)

##保存
with open('./data/query_words.json', 'w') as f:
    json.dump(query_words,f,ensure_ascii=False)

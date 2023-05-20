import os
import time
import urllib
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from hashlib import md5
import argparse
import shutil
import base64
import json
import random
import requests


data_path = "./data"
log_path = os.path.join(data_path, 'downloadlog_soogif.txt')
finger_path = os.path.join(data_path, "fingers.json")

parser = argparse.ArgumentParser()


parser.add_argument('--clear_memory', type=bool, default=False,
	help='Clear fingers and local images. Default: False')
parser.add_argument('--query_word', type=str, default="gif",
	help='Query word. Default: gif')
parser.add_argument('--upload', type=bool, default=False,
	help='Upload gif. Default: False')
args = parser.parse_args()
 
info_json = {
    "fingers":[],
}

class BingImageSpider(object):
    def __init__(self):
        self.url = "https://www.soogif.com/search/{}"
        self.directory = "./iamges/{}"  # 存储目录  这里需要修改为自己希望保存的目录  {}不要丢
        self.upload_userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
        self.upload_header = {
            'User-Agent': self.upload_userAgent,
        }
        self.login_header = {
            'User-Agent': self.upload_userAgent,
        }
        self.ua=UserAgent()
        self.header = {'User-Agent':self.ua.random}
        # self.url_rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")
        # self.title_rule = re.compile(r"\"t\"\:\"[^\"]+")

        self.pic_number = 0 # 图像数量
        self.first_page_rule = re.compile("(\d*)-(\d*)-(\d*)-(\d*).html")
        self.last_page_rule = re.compile("\d*-(\d*)-\d*-\d*.html")
        self.session = requests.session() # 实例化session对象
        # 登录
        body = {
            "name": "doudou",
            "password": "4aff6da321b28112c279a40c9b89b6e5"
        }
        item = json.dumps(body,ensure_ascii=False)
        login_res = self.session.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/user/login/", data=item, headers=self.login_header)
        print("login_status_code:", login_res.status_code)

    # 创建存储文件夹
    def create_directory(self, name):
        self.directory = self.directory.format(name)
        # 如果目录不存在则创建
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.directory += '/{}'
 
 
    def getImage(self, url, title):
        '''从原图url中将原图保存到本地'''
        try:
            time.sleep(0.2)
            # urllib.request.urlretrieve(url, self.directory.format(title))
            self.header = {'User-Agent':self.ua.random}
            res = requests.get(url, headers=self.header, timeout=3)
            # print(res)
            if(args.upload):
                base64_data = base64.b64encode(res.content) 
                base64_str = str(base64_data, 'utf-8')
                base64_str = "data:image/gif;base64," + base64_str
                upload_body = {
                    "gif_file": base64_str,
                    "gif_name": title,
                    "gif_tag": [],
                    "gif_category": args.query_word
                }
                upload_item = json.dumps(upload_body,ensure_ascii=False)
                upload_item = upload_item.encode('utf-8')
                upload_res =  self.session.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/gif/upload/", data=upload_item, headers = self.upload_header, timeout = 3)
                print("uploadstatus_code:", upload_res.status_code)
            else:
                # print(self.directory)
                # print(title)
                # print(self.directory.format(title))
                while os.path.exists(self.directory.format(title)):
                    # print("origin name: ", filename)
                    title = title[:-4]+str(random.randint(0,9)) + ".gif"
                    # print("new name: ", filename)
                with open(self.directory.format(title), "wb") as f:
                    f.write(res.content)
                    print("存储路径：" + self.directory.format(title))
            self.pic_number += 1
        except Exception as e:
            time.sleep(0.5)
            print("本张图片获取异常，跳过...")
 
 
    def findImgUrlFromHtml(self, url):
        '''从缩略图列表页中找到原图的url，并返回这一页的图片数量'''
        try: 
            self.header = {'User-Agent':self.ua.random}
            page = urllib.request.Request(url,headers=self.header)
            html = urllib.request.urlopen(page,timeout=3)
            soup = BeautifulSoup(html, "lxml")
            img_list = soup.html.body.find("div",class_="search-wrapper").find("div",class_="search-container").find_all("a",class_="image-item")[1:]
            for img_element in img_list:
                img_attrs = img_element.img.attrs
                if("src" in img_attrs):
                    gif_url = img_attrs["src"]
                    # print("gif_url: ", gif_url)
                    gif_name = img_element.find("div", class_="item-labels").span.text
                    s = md5()
                    #加密url，需要是字节串
                    s.update(gif_url.encode())
                    # 生成指纹，获取十六进制加密字符串，
                    finger = s.hexdigest()
                    if finger not in info_json["fingers"]:
                        title = gif_name.replace(" ","_").replace("/","-") + ".gif"
                        # print(title)
                        #打开高清图片网址
                        self.getImage(gif_url, title)
                        info_json["fingers"].append(finger)
        except Exception as r:
            print(r)
        #完成一页，继续加载下一页
        return
    
    def getPageLinkList(self, key):
        '''获取翻页的所有link'''
        page_link_list = []
        try:
            self.header = {'User-Agent':self.ua.random}
            page = urllib.request.Request(self.url.format(key),headers=self.header)
            html = urllib.request.urlopen(page,timeout=2)
            soup = BeautifulSoup(html, "lxml")
            # with open("./html.html",'w') as f:
            #     print(soup.prettify(), file=f)
            link_list = soup.html.body.find("div",class_="search-pagination").find_all("a")
            if(len(link_list) > 1):
                first_href=link_list[0].attrs["href"]
                last_href=link_list[-2].attrs["href"]
                page_num = int(self.last_page_rule.match(last_href).groups()[0])
                if (page_num > 15):
                    page_num = 15
                numbers = list(self.first_page_rule.match(first_href).groups())
                # print("len: ",len)
                # print(numbers)
                for pagenum in range(1,page_num+1):
                    numbers[1] = str(pagenum)
                    # print("-".join(numbers))
                    page_link_list.append("https://www.soogif.com/gif/" + "-".join(numbers) + ".html")
            else:
                page_link_list.append(self.url.format(key))
            # print(page_link_list)
        except Exception as r:
            print(r)
        return page_link_list
    
    def run(self):
        searchName = args.query_word    #图片关键词
        self.create_directory(searchName)
        searchName_parse = urllib.parse.quote(searchName)
        
        page_link_list = self.getPageLinkList(searchName_parse)
        for page_link in page_link_list:
            self.findImgUrlFromHtml(page_link)
        if(args.upload):
            with open('uploadlog_soogif.txt', "a") as f:
                print(searchName+f"----图像上传{self.pic_number}张完成--------->\n", file=f)
        else:
            with open(log_path, "a") as f:
                print(searchName+f"----图像下载{self.pic_number}张完成--------->\n", file=f)
    
 
if __name__ == '__main__':
    spider = BingImageSpider()
    if(args.clear_memory):
        if os.path.exists(finger_path):
            os.remove(finger_path)
        if os.path.exists("./iamges/{}/".format(args.query_word)):
            shutil.rmtree("./iamges/{}/".format(args.query_word))


    ##读取
    if os.path.exists(finger_path):
        with open(finger_path,"r") as f:   #设置文件对象
            info_json = json.load(f)    
        # print(info_json["fingers"])

    spider.run()

        ##保存
    with open(finger_path, 'w') as f:
        json.dump(info_json,f,ensure_ascii=False)
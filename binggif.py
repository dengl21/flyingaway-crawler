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
import random
import json
import requests

data_path = "./data"
log_path = os.path.join(data_path, 'downloadlog_bing.txt')
finger_path = os.path.join(data_path, "fingers.json")


parser = argparse.ArgumentParser()

parser.add_argument('--countNum', type=int, default=100,
	help='Picture number for crawling. Default: 100')
parser.add_argument('--start_count', type=int, default=1,
	help='Start picture number for crawling. Default: 0')
parser.add_argument('--loadNum', type=int, default=35,
	help='Picture number for one run. Default: 35')
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
        self.url = "https://cn.bing.com/images/async?q={0}&first={1}&count={2}&scenario=ImageBasicHover&datsrc=N_I&layout=ColumnBased&mmasync=1&dgState=c*9_y*2226s2180s2072s2043s2292s2295s2079s2203s2094_i*71_w*198&IG=0D6AD6CBAF43430EA716510A4754C951&SFX={3}&iid=images.5599"
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
        self.url_rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")
        self.title_rule = re.compile(r"\"t\"\:\"[^\"]+")

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
 
 
    def getImage(self, url, title, count):
        '''从原图url中将原图保存到本地'''
        try:
            time.sleep(0.2)
            # urllib.request.urlretrieve(url, self.directory.format(title))
            # print(url)
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
                while os.path.exists(self.directory.format(title)):
                    # print("origin name: ", filename)
                    title = title[:-4]+str(random.randint(0,9)) + ".gif"
                    # print("new name: ", filename)
                with open(self.directory.format(title), "wb") as f:
                    f.write(res.content)
                    print("存储路径：" + self.directory.format(title))
        except Exception as e:
            time.sleep(0.5)
            print("本张图片获取异常，跳过...")
 
 
    def findImgUrlFromHtml(self, html, count):
        '''从缩略图列表页中找到原图的url，并返回这一页的图片数量'''
        soup = BeautifulSoup(html, "lxml")
        # with open("./strhtml.html",'w') as f:
        #     print(soup.prettify(), file=f)
        link_list = soup.find_all("a", class_="iusc")
        url = []
        for link in link_list:
            url_result = re.search(self.url_rule, str(link))
            if not url_result:
                print("not url_result: ", url_result)
                continue
            # print("result: ", result.group())
            #将字符串"amp;"删除
            url = url_result.group(0)
            #组装完整url
            url = url[8:len(url)]

            s = md5()
            #加密url，需要是字节串
            s.update(url.encode())
            # 生成指纹，获取十六进制加密字符串，
            finger = s.hexdigest()
            if finger not in info_json["fingers"]:
                title_result = re.search(self.title_rule, str(link))
                # print("result: ", result.group())
                #将字符串"amp;"删除
                title = title_result.group(0)
                #组装完整url
                title = title[5:len(title)].replace(" ","_").replace("/","-") + ".gif"
                # print(title)
                #打开高清图片网址
                self.getImage(url, title, count)
                count += 1
                info_json["fingers"].append(finger)
        #完成一页，继续加载下一页
        return count
 
 
    def getStartHtml(self, key, first, loadNum, sfx):
        '''获取缩略图列表页'''
        try:
            self.header = {'User-Agent':self.ua.random}
            page = urllib.request.Request(self.url.format(key, first, loadNum, sfx),headers=self.header)
            html = urllib.request.urlopen(page,timeout=2)
        except Exception as r:
            print(r)
            html = None
        return html
    
    def run(self):
        searchName = args.query_word    #图片关键词
        self.create_directory(searchName)
        countNum = args.countNum  #爬取数量
        searchName_parse = urllib.parse.quote(searchName)
        first = args.start_count
        loadNum = args.loadNum
        sfx = 1
        count = 0
        while count < countNum:
            html = self.getStartHtml(searchName_parse, first, loadNum, sfx)
            # print(html)
            if(html):
                count = self.findImgUrlFromHtml(html, count)
            first = first + loadNum
            sfx += 1
        if(args.upload):
            with open('uploadlog_bing.txt', "a") as f:
                print(searchName+f"----图像上传{count}张完成--------->\n", file=f)
        else:
            with open(log_path, "a") as f:
                print(searchName+f"----图像下载{count}张完成--------->\n", file=f)
 
if __name__ == '__main__':
    spider = BingImageSpider()
    if(args.clear_memory):
        if os.path.exists(finger_path):
            os.remove(finger_path)
        if os.path.exists(f"./iamges/{args.query_word}/"):
            shutil.rmtree(f"./iamges/{args.query_word}/")


    ##读取
    if os.path.exists(finger_path):
        with open(finger_path,"r") as f:   #设置文件对象
            info_json = json.load(f)    
        # print(info_json["fingers"])

    spider.run()

        ##保存
    with open(finger_path, 'w') as f:
        json.dump(info_json,f,ensure_ascii=False)
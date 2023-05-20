# -*- coding:utf8 -*-
import requests
import json
from urllib import parse
import os
import time
from fake_useragent import UserAgent
from hashlib import md5
import argparse
import shutil
import base64
import random


data_path = "./data"
log_path = os.path.join(data_path, 'downloadlog_dontu.txt')
finger_path = os.path.join(data_path, "fingers.json")

parser = argparse.ArgumentParser()

parser.add_argument('--json_count', type=int, default=5,
	help='Page number for crawling. Default: 5')
parser.add_argument('--start_count', type=int, default=1,
	help='Start page number for crawling. Default: 1')
parser.add_argument('--clear_memory', type=bool, default=False,
	help='Clear fingers and local images. Default: False')
args = parser.parse_args()
parser.add_argument('--upload', type=bool, default=False,
	help='Upload gif. Default: False')
args = parser.parse_args()
info_json = {
    "fingers":[]
}

class DongtuImageSpider(object):
    def __init__(self):
        self.json_count = 0  # 请求到的json文件数量（一个json文件包含30个图像文件）
        self.url = "http://dongtu.com/hot/gif?p={}&size=15"
        self.directory = "./iamges/gif"  # 存储目录  这里需要修改为自己希望保存的目录  {}不要丢
        
        self.ua=UserAgent()
        self.header = {'User-Agent':self.ua.random}
        self.pic_number = 0 # 图像数量
        self.upload_userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
        self.login_header = {
            'User-Agent': self.upload_userAgent,
        }
        self.upload_header = {
            'User-Agent': self.upload_userAgent,
        }
        self.session = requests.session() # 实例化session对象
        # 登录
        body = {
            "name": "doudou",
            "password": "4aff6da321b28112c279a40c9b89b6e5"
        }
        item = json.dumps(body,ensure_ascii=False)
        login_res = self.session.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/user/login/", data=item, headers=self.login_header)
        print("login_status_code:", login_res.status_code)
        # with open("login_res.json","w") as f:   #设置文件对象
        #     print(login_res.text, file=f)

    # 创建存储文件夹
    def create_directory(self):
        # 如果目录不存在则创建
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.directory += '/{}'

    # 获取图像链接
    def get_image_link(self, url):
        list_image_link = []
        try:
            self.header = {'User-Agent':self.ua.random}
            strhtml = requests.get(url, headers=self.header, timeout=3)  # Get方式获取网页数据
            # with open("./strhtml.json",'w') as f:
            #     print(strhtml.text, file=f)
            jsonInfo = json.loads(strhtml.text)
            # print("len: ", len(jsonInfo['data']))
            # print(jsonInfo["data"][0])
            # print(jsonInfo)
            for index in range(15):
                gif_url = jsonInfo['data'][index]['main']
                # print("gif_url:", gif_url)
                s = md5()
                #加密url，需要是字节串
                s.update(gif_url.encode())
                # 生成指纹，获取十六进制加密字符串，
                finger = s.hexdigest()
                if finger not in info_json["fingers"]:
                    list_image_link.append(gif_url)
                    info_json["fingers"].append(finger)
            # print(list_image_link)
        except Exception as r:
            print(r)
        return list_image_link

    # 下载图片
    def save_image(self, img_link):
        # print(img_link)
        try:
            self.header = {'User-Agent':self.ua.random}
            res = requests.get(img_link, headers=self.header, timeout=5)
            if res.status_code == 404:
                print(f"图片{img_link}下载出错------->")
                return
            if not (img_link[len(img_link)-4:len(img_link)] == ".gif"):
                filename = img_link + ".gif"
            else:
                filename = img_link
            filename = filename.replace(" ","").replace("/","-")
            # print("存储路径：" + self.directory.format(filename))

            # with open(self.directory.format(filename), "wb") as f:
            #     f.write(res.content)
                
            if(args.upload):
                # 上传图片
                base64_data = base64.b64encode(res.content)
                base64_str = str(base64_data, 'utf-8')
                base64_str = "data:image/gif;base64," + base64_str
                upload_body = {
                    "gif_file": base64_str,
                    "gif_name": filename,
                    "gif_tag": [],
                    "gif_category": "动图"
                }
                upload_item = json.dumps(upload_body,ensure_ascii=False)
                upload_item = upload_item.encode('utf-8')
                upload_res =  self.session.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/gif/upload/", data=upload_item, headers = self.upload_header)
                print("uploadstatus_code:", upload_res.status_code)
            
            else:
                while os.path.exists(self.directory.format(filename)):
                    # print("origin name: ", filename)
                    filename = filename[:-4]+str(random.randint(0,9)) + ".gif"
                    # print("new name: ", filename)
                with open(self.directory.format(filename), "wb") as f:
                    f.write(res.content)
                    print("存储路径：" + self.directory.format(filename))

            self.pic_number+=1
        except Exception as r:
            print(r)

    # 入口函数
    def run(self):
        self.create_directory()

        for index in range(args.start_count, args.start_count + self.json_count):
            p = index
            request_url = self.url.format(str(p))
            list_image_link= self.get_image_link(request_url)
            for i in range(len(list_image_link)):
                self.save_image(list_image_link[i])
                time.sleep(0.2)  # 休眠0.2秒，防止封ip
        if(args.upload):
            with open('uploadlog_dontu.txt', "a") as f:
                print(f"----图像上传{self.pic_number}张完成--------->\n", file=f)
        else:
            with open(log_path, "a") as f:
                print(f"----图像下载{self.pic_number}张完成--------->\n", file=f)


if __name__ == '__main__':
    spider = DongtuImageSpider()
    spider.json_count = args.json_count   # 定义下载10组图像，也就是三百张

    if(args.clear_memory):
        if os.path.exists(finger_path):
            os.remove(finger_path)
        if os.path.exists("./iamges/gif/"):
            shutil.rmtree("./iamges/gif/")

    # if os.path.exists("info.json"):
    #     with open("info.json","r") as infofile: 
    #         info = json.load(infofile)


    ##读取
    if os.path.exists(finger_path):
        with open(finger_path,"r") as f:   #设置文件对象
            info_json = json.load(f)    
        # print(info_json["fingers"])

    spider.run()
    # print(info_json["fingers"])

    ##保存
    with open(finger_path, 'w') as f:
        json.dump(info_json,f,ensure_ascii=False)
    


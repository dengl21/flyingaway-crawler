# -*- coding:utf8 -*-
import requests
import json
from urllib import parse
import os
from fake_useragent import UserAgent
from hashlib import md5
import argparse
import shutil
import base64
import re


class Gifuploader(object):
    def __init__(self):
        self.downloaddir = "./iamges"
        self.uploaddir = "./uploaded_iamges"
        
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
        with open("login_res.json","w") as f:   #设置文件对象
            print(login_res.text, file=f)

    # 上传图片
    def uploadgif(self, img_path, move_path, filename, query_word):
        # print("img_path: ", img_path)
        # print("move_path: ", move_path)
        # print("filename: ", filename)
        try:
            with open(img_path, "rb") as imgfile:
                img_content = imgfile.read()
            # 上传图片
            base64_data = base64.b64encode(img_content)
            # print(type(base64_data))
            # 如果想要在浏览器上访问base64格式gif，需要在前面加上：data:image/gif;base64,  
            base64_str = str(base64_data, 'utf-8')
            base64_str = "data:image/gif;base64," + base64_str
            # print(base64_data)
            upload_body = {
                "gif_file": base64_str,
                "gif_name": filename,
                "gif_tag": [query_word],
                "gif_category": query_word
            }
            # print(upload_body)
            # print(self.upload_header)
            upload_item = json.dumps(upload_body,ensure_ascii=False)
            upload_item = upload_item.encode('utf-8')
            upload_res =  self.session.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/gif/upload/", data=upload_item, headers = self.upload_header, timeout = 10)
            # print("uploadstatus_code:", upload_res.status_code)
            # print("uploadstatus_code:", upload_res.text)
            if (upload_res.status_code == 200):
                shutil.copyfile(img_path, move_path)
                print("上传成功: ", img_path)
                self.pic_number+=1
            elif (upload_res.status_code == 400):
                print("上传失败: ", upload_res.status_code, upload_res.json()["msg"], img_path)
                os.remove(img_path)
            else:
                print("upload status_code:", upload_res.status_code)
        except Exception as r:
            print(r)

    def fix_query_word(self, query_word):
        if (query_word == "体育" or query_word == "运动"):
            query_word = "体育运动"
        elif (query_word == "动物"):
            query_word = "动物世界"
        elif (query_word == "猫"):
            query_word = "动物世界"
        elif (query_word == "狗"):
            query_word = "动物世界"
        elif (query_word == "鸭"):
            query_word = "动物世界"
        elif (query_word == "影视"):
            query_word = "影视片段"
        elif (query_word == "电影"):
            query_word = "影视片段"
        elif (query_word == "电视剧"):
            query_word = "影视片段"
        else:
            query_word = "gif"
        return query_word

    # 入口函数
    def run(self):
        imgdir_list = os.listdir(self.downloaddir)
        rule = re.compile("..*gif$")
        for imgdir in imgdir_list:
            if rule.match(imgdir):
                query_word = imgdir[:-4] 
                # print("match: ", query_word)
            else :
                query_word = imgdir
                # print("not match: ", query_word)
            query_word = self.fix_query_word(query_word)
            # print("query_word: ", query_word)
            download_subdir = os.path.join(self.downloaddir,imgdir)
            upload_subdir = os.path.join(self.uploaddir,query_word)
            img_name_list = os.listdir(download_subdir)
            # print("imgdir: ", imgdir)
            # print("query_word: ", query_word)
            # print("download_subdir: ", download_subdir)
            # print("upload_subdir: ", upload_subdir)

            if not os.path.exists(upload_subdir):
                os.makedirs(upload_subdir)
            
            for img_name in img_name_list:
                img_path = os.path.join(download_subdir,img_name)
                move_path = os.path.join(upload_subdir,img_name)
                if not os.path.exists(move_path):
                    self.uploadgif(img_path, move_path, img_name, query_word)

            with open('uploadlog.txt', "a") as f:
                print(imgdir+f"----图像上传{self.pic_number}张完成--------->\n", file=f)

if __name__ == '__main__':
    uploader = Gifuploader()
    uploader.run()


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
import random
import base64

data_path = "./data"
log_path = os.path.join(data_path, 'downloadlog_baidu.txt')
finger_path = os.path.join(data_path, "fingers.json")

parser = argparse.ArgumentParser()

parser.add_argument('--json_count', type=int, default=5,
	help='Page number for crawling. Default: 5')
parser.add_argument('--start_count', type=int, default=0,
	help='Start page number for crawling. Default: 0')
parser.add_argument('--clear_memory', type=bool, default=False,
	help='Clear fingers and local images. Default: False')
parser.add_argument('--query_word', type=str, default="gif",
	help='Query word. Default: gif')
parser.add_argument('--upload', type=bool, default=False,
	help='Upload gif. Default: False')
args = parser.parse_args()

info_json = {
    "fingers":[]
}

class BaiduImageSpider(object):
    def __init__(self):
        self.json_count = 0  # 请求到的json文件数量（一个json文件包含30个图像文件）
        self.url = "https://image.baidu.com/search/acjson?tn=resultjson_com&logid=11297287096844642526&ipn=rj&ct=201326592&is=&fp=result&fr=&word={}&queryWord={}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&hd=&latest=&copyright=&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&expermode=&nojc=&isAsync=&pn={}&rn=30&gsm=1e&1683713093159="
        self.directory = "./iamges/{}"  # 存储目录  这里需要修改为自己希望保存的目录  {}不要丢
        
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
    def create_directory(self, name):
        self.directory = self.directory.format(name)
        # 如果目录不存在则创建
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.directory += '/{}'

    # 获取图像链接
    def get_image_link(self, url):
        list_image_link = []
        list_image_name = []
        try:
            self.header = {'User-Agent':self.ua.random}
            strhtml = requests.get(url, headers=self.header, timeout=5)  # Get方式获取网页数据
            # with open("./strhtml.json",'w') as f:
            #     print(strhtml.text, file=f)
            jsonInfo = json.loads(strhtml.text)
            # print(jsonInfo["data"][0])
            # print(jsonInfo)
            for index in range(30):
                if(jsonInfo['data'][index]['type']=="gif"):
                    gif_url = jsonInfo['data'][index]['replaceUrl'][0]["ObjURL"]
                    s = md5()
                    #加密url，需要是字节串
                    s.update(gif_url.encode())
                    # 生成指纹，获取十六进制加密字符串，
                    finger = s.hexdigest()
                    if finger not in info_json["fingers"]:
                        list_image_link.append(gif_url)
                        list_image_name.append(jsonInfo['data'][index]['fromPageTitle'].replace(" ","_").replace("/","-"))
                        info_json["fingers"].append(finger)
            # print(list_image_name)
        except Exception as r:
            print(r)
        return list_image_link,list_image_name

    # 下载图片
    def save_image(self, img_link, filename):
        # print(img_link)
        try:
            self.header = {'User-Agent':self.ua.random}
            res = requests.get(img_link, headers=self.header, timeout=3)
            if res.status_code == 404:
                print(f"图片{img_link}下载出错------->")
                return

            if(args.upload):
                # 上传图片
                base64_data = base64.b64encode(res.content)
                # print(type(base64_data))
                # 如果想要在浏览器上访问base64格式gif，需要在前面加上：data:image/gif;base64,  
                base64_str = str(base64_data, 'utf-8')
                base64_str = "data:image/gif;base64," + base64_str
                # print(base64_data)
                upload_body = {
                    "gif_file": base64_str,
                    "gif_name": filename,
                    "gif_tag": [],
                    "gif_category": args.query_word
                }
                # print(upload_body)
                # print(self.upload_header)
                upload_item = json.dumps(upload_body,ensure_ascii=False)
                upload_item = upload_item.encode('utf-8')
                upload_res =  self.session.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/gif/upload/", data=upload_item, headers = self.upload_header, timeout = 3)
                print("uploadstatus_code:", upload_res.status_code)
                # print("uploadstatus_code:", upload_res.text)
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
        searchName = args.query_word

        searchName_parse = parse.quote(searchName)  # 编码

        self.create_directory(searchName)

        for index in range(args.start_count, args.start_count + self.json_count):
            pn = (index)*30
            request_url = self.url.format(searchName_parse, searchName_parse, str(pn))
            list_image_link,list_image_name = self.get_image_link(request_url)
            for i in range(len(list_image_link)):
                self.save_image(list_image_link[i], list_image_name[i]+'.gif')
                time.sleep(0.2)  # 休眠0.2秒，防止封ip
        if(args.upload):
            with open('uploadlog_baidu.txt', "a") as f:
                print(searchName+f"----图像上传{self.pic_number}张完成--------->\n", file=f)
        else:
            with open(log_path, "a") as f:
                print(searchName+f"----图像下载{self.pic_number}张完成--------->\n", file=f)

if __name__ == '__main__':
    spider = BaiduImageSpider()
    spider.json_count = args.json_count   # 定义下载10组图像，也就是三百张

    if(args.clear_memory):
        if os.path.exists(finger_path):
            os.remove(finger_path)
        if os.path.exists("./iamges/{}/".format(args.query_word)):
            shutil.rmtree("./iamges/{}/".format(args.query_word))

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
    


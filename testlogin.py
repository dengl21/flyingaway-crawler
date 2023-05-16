import requests
import json

upload_userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
login_header = {
    # "Accept":"application/json, text/plain, */*",
    # "Accept-Encoding":"gzip, deflate",
    # "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    # "Connection": "keep-alive",
    # "Content-Length":"60",
    # "Content-Type": "application/json",
    # "Cookie": "csrftoken=YOMPAOBR3FIuLmDP1RpuKRQUTxqRPrzo",
    # "Host": "frontend-flyingaway.app.secoder.net",
    # "Origin": "http://frontend-flyingaway.app.secoder.net",
    # "Referer": "http://frontend-flyingaway.app.secoder.net/login",
    'User-Agent': upload_userAgent,
}

# # 注册
# register_body = {
#     "name": "dou",
#     "password": "Dou510908",
#     "email": "doudou510908@126.com"
# }
# item = json.dumps(register_body,ensure_ascii=False)
# register_res = requests.post("http://127.0.0.1:8000/api/user/register/", data=item,headers=login_header)
# print("register_status_code:", register_res.status_code)
# with open("register_res.json","w") as f:   #设置文件对象
#     print(register_res.text, file=f)

# 登录
body = {
    "name": "dou",
    "password": "Dou510908"
}
item = json.dumps(body,ensure_ascii=False)
login_res = requests.post("https://flyingaway-backend-FlyingAway.app.secoder.net/api/user/login/", data=item, headers=login_header)
print("login_status_code:", login_res.status_code)
with open("login_res.json","w") as f:   #设置文件对象
    print(login_res.text, file=f)
import os
import json
from random import sample


commond = "python getquerywords.py"
print("commond: ", commond)
os.system(commond)
with open("./data/query_words.json","r") as f:   #设置文件对象
    jsoninfo = json.load(f)   
query_word_list = jsoninfo["all"]
# print(query_word_list)


basel_query_words = ["人物反应", "体育运动", "体育", "运动", "动画表情", "动物世界", "动物", "影视片段", "影视", "电影", "电视剧", "可爱", "沙雕", "食物", "综艺", "表情包", "明星", "躺平", "搞笑", "动画", "二次元", "动漫", "游戏"]
query_word_list = basel_query_words + query_word_list
query_word_list = sample(query_word_list, 10) 


for query_word in query_word_list:
    if (os.path.exists(f"./iamges/{query_word}gif")):
        continue
    query_word += "gif"
    commond = f"python baidugif.py --json_count 20 --query_word {query_word}"
    print("commond: ", commond)
    os.system(commond)
    # break

for query_word in query_word_list:
    if (os.path.exists(f"./iamges/{query_word}gif")):
        continue
    query_word += "gif"
    commond = f"python binggif.py --countNum 100 --query_word {query_word}"
    print("commond: ", commond)
    os.system(commond)
    # break

for query_word in query_word_list:
    if (os.path.exists(f"./iamges/{query_word}")):
        continue
    commond = f"python soogif.py --query_word  {query_word}"
    print("commond: ", commond)
    os.system(commond)
    break

commond = "python dongtugif.py  --json_count 50"
print("commond: ", commond)
os.system(commond)

commond = "python vsgif.py  --json_count 50"
print("commond: ", commond)
os.system(commond)

commond = "python upload.py"
print("commond: ", commond)
os.system(commond)

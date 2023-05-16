import os
import json
from random import sample
# query_word_list = ["人物反应", "体育运动", "体育", "运动", "动画表情", "动物", "狗", "鸭", "猫", "影视", "电影", "电视剧","可爱", "沙雕", "食物", "综艺", "表情包"]

with open("query_words.json","r") as f:   #设置文件对象
    query_word_list = json.load(f)   

query_word_list = sample(query_word_list, 20) 

print(query_word_list)
        # print(info_json["fingers"])


# query_word_list = ["跑步", "滑冰", "游泳", "跳高", "体操", "举重", "冲浪", "自行车", "", "瑜伽", "健身", "跳高", "体操", "举重", "体操", "自行车", "电影", "电视剧"]

# for query_word in query_word_list:
#     query_word += "gif"
#     commond = f"python baidugif.py --json_count 20 --query_word {query_word}"
#     print("commond: ", commond)
#     os.system(commond)

for query_word in query_word_list:
    query_word += "gif"
    commond = f"python binggif.py --countNum 100 --query_word {query_word}"
    print("commond: ", commond)
    os.system(commond)

for query_word in query_word_list:
    commond = f"python soogif.py --query_word  {query_word}"
    print("commond: ", commond)
    os.system(commond)

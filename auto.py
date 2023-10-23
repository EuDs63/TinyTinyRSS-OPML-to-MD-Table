import xml.etree.ElementTree as ET
import requests
import json
import os
import re
from datetime import date
import sys

# 路径
root_path = os.path.dirname(__file__)

# 读取config
if len(sys.argv) > 1:
    if sys.argv[1] == 'dev':
        # 从config.json中读取
        config_path = os.path.join(root_path,'config.json')
        with open(config_path,'r') as f:
            config = json.load(f)
    elif sys.argv[1] == 'prod':
        # 从secret中读取
        secrets_json = os.environ['MY_CONFIG_JSON']
        config = json.loads(secrets_json)
else:
    # 默认从config.json中读取
    config_path = os.path.join(root_path,'config.json')
    with open(config_path,'r') as f:
        config = json.load(f)


baseUrl = config['baseUrl']
user = config['user']
password = config['password']

# 构造登录请求，获取 Session ID
headers = {'Content-Type': 'application/json'}
loginUrl = f"{baseUrl}api/"
data = {'op': 'login', 'user': user, 'password': password}

response = requests.post(loginUrl, headers=headers, data=json.dumps(data))
session_id = response.json()['content']['session_id']

#构造获取 OPML 文件的请求，附带 Session ID
opmlUrl = f"{baseUrl}backend.php?op=opml&method=export"
response = requests.get(opmlUrl, cookies={'ttrss_sid': session_id})

# 获取当前日期
today = date.today()
today_str = today.strftime("%Y-%m-%d")

# 输出ompl文件
OpmlName = f"feed_{today_str}.opml"
OpmlPath = os.path.join(root_path,"Opml",OpmlName)
with open(OpmlPath, 'wb') as f:
    f.write(response.content)

# 解析opml文件
tree = ET.parse(OpmlPath)
root = tree.getroot()

outlines = []

for outline in root.findall('.//outline'):
    title = outline.get('text')
    feed_url = outline.get('xmlUrl')
    html_url = outline.get('htmlUrl')
    if feed_url:
        outlines.append({'title': title, 'feed_url': feed_url,'html_url': html_url})

md_text = f"**更新时间：{today}**\n"
md_table = "| Title | Feed URL | Html URL|\n| --- | --- | --- |\n"

# json文件的输出
data = []

for outline in outlines:
    md_table += f"| {outline['title']} | {outline['feed_url']} | {outline['html_url']}|\n"
    item = {
        "title": outline['title'],
        "feed_url": outline['feed_url'],
        "html_url": outline['html_url']
    }
    data.append(item)

# 输出为Markdown文件
MarkdownName = f"feed_{today_str}.md"
MarkdownPath = os.path.join(root_path,"Markdown",MarkdownName)
with open(MarkdownPath,'w',encoding='utf-8') as f:
    f.write(md_text)
    f.write(md_table)

# 输出为JSON文件
output_data = {
    "data": data,
    "last_updated": today_str,  # 添加当前时间的时间戳
    "count": len(outlines)
}

JsonName = f"feed_{today_str}.json"
JsonPath = os.path.join(root_path,"Json",JsonName)
with open(JsonPath,'w',encoding='utf-8') as f:
    json.dump(output_data,f,ensure_ascii=False,indent=4)

JsonPath2 = os.path.join(root_path, "rss_subscription.json")
with open(JsonPath2,'w',encoding='utf-8') as f:
    json.dump(output_data,f,ensure_ascii=False,indent=4)

# 打开README.md文件
readme_path = os.path.join(root_path,"README.md")
replace = '## 我的订阅\n'+md_text + md_table+'\n'



# 替换README.md中我的订阅之后的内容，以实时更新

## 方法1 ： 逐行读取，定位到标题行，从标题行开始写入替换内容，覆盖原内容
with open(readme_path, 'r+',encoding='utf-8') as f:
    line = f.readline()
    while line:
        if '## 我的订阅\n' in line:
            title_pos = f.tell()  # 使用f.tell()记录标题行位置
            #print(title_pos)
            f.seek(title_pos)   # 定位到标题行位置
            replace2 = md_text + md_table+'\n'
            f.write(replace2)
            break
        line = f.readline()

## 不知道为什么不行
# with open(readme_path, 'r+',encoding='utf-8') as f:
#     #f.seek(0)
#     line = f.readline()
#     line_num = 1
#     while line:
#         if '## 我的订阅\n' in line:
#             start_line_num = line_num  # 记录所在行号
#             print(f.tell())
#             f.seek(0)  # 重新定位到文件开头
#             print(f.tell())
#             for i in range(start_line_num):
#                 f.readline()  # 读取到标题所在行
#             # 此时文件指针位于所需位置,可以执行写入操作
#             print(f.tell())
#             f.seek(f.tell())   # 定位到标题行位置
#             f.write(replace)
#             print(f.tell())
#             break
#         line = f.readline()
#         line_num += 1

## 方法2：正则表达式实现
# with open(readme_path,'r',encoding='utf-8') as f:
#     readme = f.read()
# pattern = r'## 我的订阅(.*)\n'
# readme = re.sub(pattern,replace,readme,flags=re.DOTALL)
# with open(readme_path,'w',encoding='utf-8') as f:
#     f.write(readme)

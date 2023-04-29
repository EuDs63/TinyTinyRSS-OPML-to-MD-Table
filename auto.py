import xml.etree.ElementTree as ET
import requests
import json
import os
from datetime import date

# 路径
root_path = os.path.dirname(__file__)

# 读取config
## 从config.json中读取
# config_path = os.path.join(root_path,'config.json')
# with open(config_path,'r') as f:
#     config = json.load(f)
## 从secret中读取
secrets_json = os.environ['MY_CONFIG_JSON']
config = json.loads(secrets_json)
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
OpmlName = f"feed_{today_str}.opml"
OpmlPath = os.path.join(root_path,OpmlName)
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

md_links = []
for outline in outlines:
    md_link = f"[{outline['title']}]({outline['feed_url']})"
    md_links.append(md_link)

md_text = "\n".join(md_links)

md_table = "| Title | Feed URL | Html URL|\n| --- | --- | --- |\n"

for outline in outlines:
    md_table += f"| {outline['title']} | {outline['feed_url']} | {outline['html_url']}|\n"

# 输出为Markdown文件
MarkdownName = f"feed_{today_str}.md"
MarkdownPath = os.path.join(root_path,MarkdownName)
with open(MarkdownPath,'w',encoding='utf-8') as f:
    f.write(md_table)




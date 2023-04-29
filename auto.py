import xml.etree.ElementTree as ET
import requests
import json
import os
from datetime import date

today_str = date.today().strftime('%Y-%m-%d')

# Load configuration from JSON file
root_path = os.path.dirname(__file__)
secrets_json = os.environ['MY_CONFIG_JSON']
config = json.loads(secrets_json)

# Login to get session ID
login_url = f"{config['baseUrl']}api/"
login_data = {'op': 'login',
              'user': config['user'],
              'password': config['password']}
login_headers = {'Content-Type': 'application/json'}
response = requests.post(login_url,
                         headers=login_headers,
                         json=login_data)
session_id = response.json()['content']['session_id']

# Download OPML file and save to disk
opml_url = f"{config['baseUrl']}backend.php?op=opml&method=export"
opml_response = requests.get(opml_url,
                             cookies={'ttrss_sid': session_id})
opml_name = f"feed_{today_str}.opml"
opml_path = os.path.join(root_path, "Opml", opml_name)
with open(opml_path, 'wb') as f:
    f.write(opml_response.content)

# Parse OPML file and generate Markdown file
root = ET.parse(OpmlPath).getroot()

outlines = [
    {
        'title': outline.get('text'),
        'feed_url': outline.get('xmlUrl'),
        'html_url': outline.get('htmlUrl'),
    }
    for outline in root.iter('outline')
    if outline.get('xmlUrl')
]

md_table = (
    "| Title | Feed URL | Html URL |\n"
    "| --- | --- | --- |\n"
    + "\n".join(
        f"| [{outline['title']}]({outline['feed_url']}) | {outline['feed_url']} | {outline['html_url']}|"
        for outline in outlines
    )
)

md_path = os.path.join(root_path, "Markdown", f"feed_{today_str}.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_table)

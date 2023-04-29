import xml.etree.ElementTree as ET

tree = ET.parse('Projects\opml\my_tiny_tiny_rss.xml.xml')
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

with open('Projects\opml\my_tiny_tiny_rss.xml.md','w',encoding='utf-8') as f:
    f.write(md_table)


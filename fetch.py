from lxml import html
import requests


PATTERN = "https://www.flickr.com/photos/liikennevirasto/albums/"
DOMAIN = "https://www.liikennevirasto.fi"


def fetch(path):
    page = requests.get(DOMAIN + path)
    return html.fromstring(page.content)


"""
tree = fetch("/web/en/road-network/traffic-signs")

sections = tree.xpath('//div[@class="section-content"]')

urls = []

for section in sections:
    urls += section.xpath('*/a/@href')
    urls += section.xpath('a/@href')

hrefs = []
for url in urls:
    print("Proc: " + url)
    page = fetch(url)
    hrefs += [
        href for href in page.xpath("//a/@href") if href.startswith(PATTERN)
    ]

"""

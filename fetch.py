import json
from lxml import html
import requests
from pprint import pprint


PATTERN = "https://www.flickr.com/photos/liikennevirasto/albums/"
DOMAIN = "https://www.liikennevirasto.fi"

"""
def fetch(path):
    return html.fromstring(requests.get(DOMAIN + path).content)


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

print(hrefs)
"""


def remove_prefix(string, prefix):
    return string[len(prefix):] if string.startswith(prefix) else string


def remove_suffix(string, suffix):
    return string[:-len(suffix)] if string.endswith(suffix) else string


resp = requests.get("https://api.flickr.com/services/rest", {
    "method": "flickr.photosets.getPhotos",
    "api_key": "2f0e634b471fdb47446abcb9c5afebdc",
    "photoset_id": "72157658087746553",
    "extras": "description,url_q",
    "format": "json"
})

text = remove_suffix(
    remove_prefix(resp.text, "jsonFlickrApi("),
    ")"
)
data = json.loads(text).get("photoset").get("photo")

pprint(data)
"""
https://api.flickr.com/services/rest/?=&format=json&jsoncallback=jQuery111307133405740796193_1529785762116&_=1529785762117

URL = "https://www.flickr.com/photos/liikennevirasto/sets/72157658087746553"
doc = requests.get(URL).text
print(doc.split("\n"))

"""
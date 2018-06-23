import json
from lxml import html
import requests
from pprint import pprint


PATTERN = "https://www.flickr.com/photos/liikennevirasto/albums/"
DOMAIN = "https://www.liikennevirasto.fi"

def fetch(path):
    return html.fromstring(requests.get(DOMAIN + path).content)


def remove_prefix(string, prefix):
    return string[len(prefix):] if string.startswith(prefix) else string


def remove_suffix(string, suffix):
    return string[:-len(suffix)] if string.endswith(suffix) else string


tree = fetch("/web/en/road-network/traffic-signs")

sections = tree.xpath('//div[@class="section-content"]')

urls = []

for section in sections:
    urls += section.xpath('*/a/@href')
    urls += section.xpath('a/@href')

ids = []
for url in urls:
    page = fetch(url)
    ids += [
        remove_prefix(href, PATTERN) for href in page.xpath("//a/@href") if href.startswith(PATTERN)
    ]





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

photos = []

for item in json.loads(text).get("photoset").get("photo"):
    desc = item.get("description").get("_content")
    parts = desc.split("\n")
    title = parts[1]
    url = item.get("url_q")
    photos.append(dict(
        title=title,
        url=url
    ))

pprint(photos)

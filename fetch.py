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


def download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


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


def get_photos(pk):
    resp = requests.get("https://api.flickr.com/services/rest", {
        "method": "flickr.photosets.getPhotos",
        "api_key": "2f0e634b471fdb47446abcb9c5afebdc",
        "photoset_id": pk,
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
        if len(parts) >= 2:
            title = parts[1]
        elif parts:
            title = parts[0]
        else:
            title = "UNKNOWN"
        url = item.get("url_q")
        photos.append(dict(
            title=title,
            url=url
        ))
    return photos

import os
os.chdir("cards")

fetched = []
for pk in ids:
    for photo in get_photos(pk):
        print(photo)
        name = download_file(photo["url"])
        fetched.append(dict(
            title=photo["title"],
            name=name
        ))

with open("index.json", "w") as fil:
    json.dump(fetched, fil)

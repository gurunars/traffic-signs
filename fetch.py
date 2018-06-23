import json
from lxml import html
import requests
import os
from pprint import pprint
import genanki


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
    if os.path.exists(local_filename):
        return local_filename
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


tree = fetch("/web/en/road-network/traffic-signs")

sections = tree.xpath('//div[@class="section-content"]')

links = []

for section in sections:
    links += section.xpath('*/a')
    links += section.xpath('a')

links = [
    {
        "title": link.xpath("text()")[0],
        "url": link.xpath("@href")[0]
    }
    for link in links
]

sections = []
for link in links:
    page = fetch(link["url"])
    sections.append({
        "title": link["title"],
        "id": [
            remove_prefix(href, PATTERN)
            for href in page.xpath("//a/@href") if href.startswith(PATTERN)
        ][0]
    })


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

decks = []
for section in sections:
    fetched = []
    for photo in get_photos(section["id"]):
        print(photo)
        title = photo["title"]
        if title.startswith("<a href="):
            title = "UNKNOWN"
        name = download_file(photo["url"])
        fetched.append(dict(
            title=title,
            name=name
        ))
    decks.append({
        "title": section["title"],
        "cards": fetched
    })


count = 1
card_count = 1
for deck in decks:
    genanki.Deck(count, deck["title"])
    count += 1
    for card in deck["cards"]:
        card_count += 1

"""
import codecs
payload = json.dumps(deck, ensure_ascii=False, indent=2)
with codecs.open("index.json", "w", encoding="utf-8") as fil:
    fil.write(payload)
"""
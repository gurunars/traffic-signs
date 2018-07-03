import json
from lxml import html
import requests as raw_requests
import os
from pprint import pprint
import shutil
from googletrans import Translator
import hashlib
import jinja2

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

CARDS = ".cards"
CACHE = ".cache"
TRANS = ".trans"

requests = CacheControl(
    raw_requests.Session(),
    cache=FileCache(CACHE, forever=True)
)

translator = Translator()

PATTERN = "https://www.flickr.com/photos/liikennevirasto/albums/"
DOMAIN = "https://www.liikennevirasto.fi"
# random.randrange(1 << 30, 1 << 31)
DECK_ID = 1287472585
MODEL_ID = 1180172397


def get_hash(string):
    return hashlib.sha224(string.encode('utf-8')).hexdigest()


def translate(string):
    os.makedirs(TRANS, exist_ok=True)
    path = os.path.join(TRANS, get_hash(string))
    if os.path.exists(path):
        with open(path) as fil:
            return fil.read()
    value = translator.translate(string).text
    with open(path, "w") as fil:
        fil.write(value)
    return value


def fetch(path):
    return html.fromstring(requests.get(DOMAIN + path).content)


def remove_prefix(string, prefix):
    return string[len(prefix):] if string.startswith(prefix) else string


def remove_suffix(string, suffix):
    return string[:-len(suffix)] if string.endswith(suffix) else string


def get_sections():
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
    return sections


def get_photos(pk):
    resp = requests.get("https://api.flickr.com/services/rest", params={
        "method": "flickr.photosets.getPhotos",
        "api_key": "2f0e634b471fdb47446abcb9c5afebdc",
        "photoset_id": pk,
        "extras": "description,url_m,url_o,url_q",
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
            title = None
        print("Processing photo {}".format(title))
        if title and not title.startswith("<a href="):
            title = translate(title)
        else:
            title = "UNKNOWN"

        url = item.get("url_m") or item.get("url_o") or item.get("url_q")
        photos.append(dict(
            guid=pk,
            title=title.strip(),
            image=url
        ))
    return photos


TEMPLATE = """
<html>
    <head>
        <title>Finnish Traffic Signs</title>
    </head>
    <body>
        {% for section in sections %}
        <h1>{{section.title}}</h1>
            {% for sign in section.signs %}
                <div>
                    <img src={{sign.image}} />
                    <p>{{sign.title}}</p>
                </div>
                <hr/>
            {% endfor %}
        {% endfor %}
    </body>
</html>
"""


def generate_package():
    if not os.path.exists(CARDS):
        os.mkdir(CARDS)

    os.chdir(CARDS)

    sections = []

    for section in get_sections():
        print("Processing section {}".format(section["title"]))
        sections.append({
            "title": section["title"],
            "signs": get_photos(section["id"])
        })

    tpl = jinja2.Template(TEMPLATE)
    with open("index.html", "w") as fil:
        fil.write(tpl.render({"sections": sections}))

generate_package()

import json
from lxml import html
import requests as raw_requests
import os
from pprint import pprint
import genanki
import shutil
from googletrans import Translator
import hashlib

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

CARDS = ".cards"
CACHE = ".cache"
TRANS = ".trans"
NAME = 'finnish_traffic_signs.apkg'

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
    os.makedirs(os.path.join(CARDS, TRANS), exist_ok=True)
    key = get_hash(string)
    path = os.path.join(CARDS, TRANS, key)
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
            title = None

        if title and not title.startswith("<a href="):
            title = translate(title)
        else:
            title = "UNKNOWN"

        url = item.get("url_q")
        photos.append(dict(
            guid=pk,
            title=title.strip(),
            url=url
        ))
    return photos


def generate_package():
    if not os.path.exists(CARDS):
        os.mkdir(CARDS)

    os.chdir(CARDS)

    model = genanki.Model(
        MODEL_ID,
        'Images with descriptions',
        fields=[
            {'name': 'Description'},
            {'name': 'Image'},
        ],
        templates=[
            {
            'name': 'Image Card',
            'qfmt': '{{Description}}',
            'afmt': '{{FrontSide}} <hr id=answer> {{Image}}',
            },
        ]
    )

    deck = genanki.Deck(DECK_ID, "Finnish Traffic Signs")
    images = []

    for section in get_sections():
        for photo in get_photos(section["id"]):
            print(photo)
            title = photo["title"]
            image = download_file(photo["url"])
            images.append(image)
            deck.add_note(genanki.Note(
                guid=photo["guid"],
                model=model,
                fields=[ title, '<img src="{}" />'.format(image) ],
                tags=[section["title"]]
            ))

    package = genanki.Package(deck)
    package.media_files = images
    package.write_to_file(NAME)
    if os.path.exists("../" + NAME):
        os.remove("../" + NAME)
    shutil.move(NAME, "..")

generate_package()

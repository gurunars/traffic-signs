import json
from lxml import html
import requests
import os
from pprint import pprint
import genanki


PATTERN = "https://www.flickr.com/photos/liikennevirasto/albums/"
DOMAIN = "https://www.liikennevirasto.fi"
# random.randrange(1 << 30, 1 << 31)
DECK_ID = 1287472585
MODEL_ID = 1180172397


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

deck_specs = []
for section in sections:
    fetched = []
    for photo in get_photos(section["id"]):
        title = photo["title"]
        if title.startswith("<a href="):
            title = "UNKNOWN"
        name = download_file(photo["url"])
        fetched.append(dict(
            title=title,
            name=name
        ))
    deck_specs.append({
        "title": section["title"],
        "cards": fetched
    })


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
      'afmt': '{{FrontSide}} <hr id=answer> <img src="{{Image}}">',
    },
  ])


deck = genanki.Deck(DECK_ID, "Finnish Traffic Signs")
images = []
for deck_spec in deck_specs:
    for card in deck_spec["cards"]:
        print(card)
        deck.add_note(genanki.Note(
            model=model,
            fields=[
                card["title"],
                card["name"]
            ],
            tags=[deck_spec["title"]]
        ))
        images.append(card["name"])

package = genanki.Package(deck)
package.media_files = images
package.write_to_file('finnish_traffic_signs.apkg')

"""
import codecs
payload = json.dumps(deck, ensure_ascii=False, indent=2)
with codecs.open("index.json", "w", encoding="utf-8") as fil:
    fil.write(payload)
"""
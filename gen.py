import genanki
import json
import os

os.chdir("cards")

with open("index.json") as fil:
    print(json.load(fil))

my_deck = genanki.Deck(
  2059400110,
  'Country Capitals')

my_deck.add_note(my_note)
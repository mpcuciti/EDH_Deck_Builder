import requests
import json
import pprint

# content = requests.get("https://edhrec-json.s3.amazonaws.com/en/cards/swords-to-plowshares.json")
# content = content.json()
# pprint.pprint(type(content['container']['json_dict']['cardlists'][5]['cardviews'][0]))

class mtgcard:

    def __init__(self, url):
        self.url = url
        self.clean_url(self.url)
        self.get_json(self.url)

    def clean_url(self, url):
        if self.url[0] == '/':
            self.url = 'https://edhrec.com' + self.url

    def get_json(self, url):
        if 'cards' in url:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/cards/'
        elif 'commanders' in url:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/commanders/'
        i = 0
        for each in url:
            if each == '/':
                output = i
            i += 1
        self.json_url = url_base + url[output + 1: len(url)] + '.json'
        content = requests.get(self.json_url).json()
        content = content['container']['json_dict']
        
        self.raw_dict = content
        self.cmc = int(content['card']['cmc'])
        self.type = content['card']['type']
        self.name = content['card']['name']
        if 'legal_commander' in content['card']:
            self.legal_commander = content['card']['legal_commander']
        else:
            self.legal_commander = False


        if not content['card']['color_identity']:
            self.color_id = [0]
        self.color_id = content['card']['color_identity']

        self.top_commanders = content['cardlists'][0]['cardviews']
        self.top_cards = content['cardlists'][4]['cardviews']
        
class mtgdeck:
    def __init__(self, temp_card):
        self.instantiate_deck_list()

        def instantiate_deck_list():
            if not deck_list:
                deck_list = list()
        def add_card():
            deck_list.append(temp_card)

def mana_match(color_id_1, color_id_2):
    #makes sure the mana requirements of color id 2 are met by color id 1
    if not color_id_2:
        return True
    for color in color_id_2:
        if color not in color_id_1:
            return False
    return True
def is_valid_commander(url):
    temp_card = mtgcard(url)
    if temp_card.legal_commander == True:
        return True
    elif temp_card.legal_commander == False:
        return False
    else:
        return False

    pass
def get_end_of_url(url):
    url = url[(url.find('.com') + 4): len(url)]
    return url

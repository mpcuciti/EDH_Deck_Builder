import requests
import json
import pprint

# content = requests.get("https://edhrec-json.s3.amazonaws.com/en/cards/swords-to-plowshares.json")
# content = content.json()
# pprint.pprint(type(content['container']['json_dict']['cardlists'][5]['cardviews'][0]))

class mtgcard:
    def __init__(self, url, commander=False):
        self.url = url
        if commander == False:
            self.commander = False
        elif commander == True:
            self.commander = True
        else:
            commander == False
        self.clean_url(self.url)
        self.get_json(self.url)

    def clean_url(self, url):
        if self.url[0] == '/':
            self.url = 'https://edhrec.com' + self.url

    def get_json(self, url):
        if 'cards' in url or self.commander == False:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/cards/'
        elif 'commanders' in url or self.commander == True:
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

        self.card_lists = content['cardlists']

        self.top_commanders = self.search_card_lists('Top Commanders')
        self.top_cards = self.search_card_lists('Top Cards')
        self.top_synergy = self.search_card_lists('High Synergy Cards')

    def search_card_lists(self, list_name):
        for dict in self.card_lists:
            if dict['header'] == list_name:
                return dict['cardviews']
        return None
        
class mtgdeck:
    def __init__(self, commander):
        self.commander = commander
        self.deck_list = {self.commander.name: commander}
        self.mana_curve = {}

    def mana_match(self, temp_card):
    #makes sure the card fits with the commander color identity
        if not temp_card.color_id:
            return True
        for color in temp_card.color_id:
            if color not in self.commander.color_id:
                return False
        return True

    def is_card_in_deck(self, temp_card):
        if temp_card.name in self.deck_list.keys():
            return True
        else:
            return False

    def add_card(self, temp_card):
        if self.mana_match(temp_card) == True:
            if self.is_card_in_deck(temp_card) != True:
                print('Adding', temp_card.name)
                self.deck_list[temp_card.name] = temp_card
                return True
        return None
    
    def add_top_commander_cards(self, x):
        index = 0
        number_of_cards_added = 0
        while number_of_cards_added < x and index < len(self.commander.top_cards):
            temp_card = mtgcard(self.commander.top_cards[index]['url'])
            if self.is_card_in_deck(temp_card) == True:
                index += 1
            else: 
                if(self.add_card(temp_card)) == True:
                    number_of_cards_added += 1
                index += 1
        return number_of_cards_added

    def just_add_every_related_card(self):
        for card_list in self.commander.card_lists:
            for card in card_list['cardviews']:
                temp_card = mtgcard(card['url'])
                self.add_card(
                    temp_card
                )
        return
    
    def calculate_mana_curve(self):
        self.mana_curve = {}
        for card_name, card in self.deck_list.items():
            if card.cmc in self.mana_curve.keys():
                self.mana_curve[card.cmc] += 1
            elif card.cmc not in self.mana_curve.keys():
                self.mana_curve[card.cmc] = 1
        return
    
    def get_to_x_cards(self):
        return



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

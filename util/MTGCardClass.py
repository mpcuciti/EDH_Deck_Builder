from itertools import combinations_with_replacement
import requests
import json
import random
from datetime import datetime
import math

class MTGCardClass:
    def __init__(self, url, db_info=None):
        self.url = url
        self.raw_json = None
        self.json = None

        self.name = None
        self.cmc = None
        self.color_id = None
        self.type = None
        self.legal_commander = None
        self.salt = None 
        self.related_cards = None
        self.db_info = db_info

        self.clean_url()
        self.get_card_data()
        self.parse_card_data()
        self.build_related_cards_dict()

    def clean_url(self):
        if self.url[0] == '/':
            self.short_url = self.url
            self.url = 'https://edhrec.com' + self.url
        
        if self.url[(len(self.url) - 1)] == '/':
            self.url = self.url[:-1]

        if 'cards' in self.url:
            url_base = 'https://json.edhrec.com/cards/'
        elif 'commanders' in self.url:
            url_base = 'https://json.edhrec.com/commanders/'
        #This is getting the last section of the url (the name) and combining it with the url_base and the .json to come up with the json download path
        i = 0
        for each in self.url:
            if each == '/':
                output = i
            i += 1
        self.json_url = url_base + self.url[output + 1: len(self.url)] + '.json'
        return

    def get_card_data(self):
        self.db_info = None #Eventually this will branch based on the DB being used but I'm not worrying about that during the refactor
        if self.db_info == None:
            self.raw_json = json.loads(requests.get(self.json_url).text)
            self.json = self.raw_json['container']['json_dict']
        else:
            #Do something else fancy here with DB classes. For right now it's always going to be None
            pass
        return

    def parse_card_data(self):
        self.name = self.json['card']['name']
        self.cmc = int(self.json['card']['cmc'])
        self.type = self.json['card']['primary_type']
        self.detail_type = self.json['card']['type']
        self.salt = self.json['card']['salt']
        self.color_id = self.json['card']['color_identity']
        #legal commander not always present so have to check for it
        if 'legal_commander' in self.json['card']:
            self.legal_commander = self.json['card']['legal_commander']
        else:
            self.legal_commander = False
        return

    def build_related_cards_dict(self):
        #Build lists starting here:
        card_lists = self.json['cardlists']
        url_dict = {}
        for dict in card_lists:
            for card in dict['cardviews']:
                if 'synergy' in card.keys():
                    url_dict[card['name']] = {
                        'synergy': card['synergy'], 
                        'url': card['url'], 
                        'type': card['primary_type'], 
                        'color_id': card['color_identity'], 
                        'salt': card['salt'] 
                        }
        self.related_cards = url_dict

    def select_synergistic_card(self, type_list=['Creature', 'Sorcery', 'Instant', 'Enchantment', 'Artifact', 'Planeswalker']):
        weighted_list = {}
        for name, card in self.related_cards.items():
            weighted_list[name] = card['synergy']
        choice = random.choices(list(weighted_list.keys()), list(weighted_list.values()))
        choice = choice[0]
        temp_card = MTGCardClass(self.related_cards[choice]['url'], self.db_info)

        while temp_card.type not in type_list:
            choice = random.choices(list(weighted_list.keys()), list(weighted_list.values()))
            choice = choice[0]
            temp_card =  MTGCardClass(self.related_cards[choice]['url'], self.db_info)

        return temp_card

    def select_salty_card(self):
        weighted_list = {}
        for name, card in self.related_cards.items():
            weighted_list[name] = card['salt']
        choice = random.choices(list(weighted_list.keys()), list(weighted_list.values()))
        choice = choice[0]
        temp_card = MTGCardClass(self.related_cards[choice]['url'], self.db_info)
        return temp_card
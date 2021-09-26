from itertools import combinations_with_replacement
import requests
import json
import random
from datetime import datetime
import math


class mtgcard:
    def __init__(self, url, conn):
        self.url = url
        self.conn = conn

        self.name = None
        self.cmc = None
        self.type = None
        self.legal_commander = None
        self.salt = None 

        self.related_cards = None

        self.clean_url()
        self.get_card_data()
        self.parse_card_data()
        self.build_related_cards_dict()

    def clean_url(self):
        if self.url[0] == '/':
            self.short_url = self.url
            self.url = 'https://edhrec.com' + self.url

        if 'cards' in self.url:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/cards/'
        elif 'commanders' in self.url:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/commanders/'
        #This is getting the last section of the url (the name) and combining it with the url_base and the .json to come up with the json download path
        i = 0
        for each in self.url:
            if each == '/':
                output = i
            i += 1
        self.json_url = url_base + self.url[output + 1: len(self.url)] + '.json'
        return

    def get_card_data(self):
        if self.check_if_card_in_database() != True:
            self.add_card_json_to_db()
        self.load_card_json_from_db()
        return

    def check_if_card_in_database(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mtgcard_data WHERE card_json_url = %s",
            [self.json_url]
        )
        rows = cursor.fetchall()
        cursor.close()
        if not rows:
            return False
        else:
            return True

    def add_card_json_to_db(self):
        temp_data = requests.get(self.json_url).text
        temp_name = json.loads(temp_data)['container']['json_dict']['card']['name']
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO mtgcard_data (card_name, card_json_url, card_json, timestamp) VALUES(%s, %s, %s, %s) ;",
            [temp_name, self.json_url, temp_data, datetime.now()]
        )
        self.conn.commit()
        cursor.close()
        return

    def load_card_json_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT card_json FROM mtgcard_data WHERE card_json_url = %s ;",
            [self.json_url]
            )
        row = cursor.fetchall()
        cursor.close()
        self.raw_json = dict(row[0][0])
        return

    def parse_card_data(self):
        content = self.raw_json['container']['json_dict']
        self.cmc = int(content['card']['cmc'])
        self.target_mana = int(self.raw_json['land'])
        self.type = content['card']['primary_type']
        self.detail_type = content['card']['type']
        self.name = content['card']['name']
        self.salt = content['card']['salt']
        self.color_id = content['card']['color_identity']
        #legal commander not always present so have to check for it
        if 'legal_commander' in content['card']:
            self.legal_commander = content['card']['legal_commander']
        else:
            self.legal_commander = False
        return

    def build_related_cards_dict(self):
        #Build lists starting here:
        content = self.raw_json['container']['json_dict']
        card_lists = content['cardlists']
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
        temp_card = mtgcard(self.related_cards[choice]['url'], conn=self.conn)

        while temp_card.type not in type_list:
            choice = random.choices(list(weighted_list.keys()), list(weighted_list.values()))
            choice = choice[0]
            temp_card = mtgcard(self.related_cards[choice]['url'], conn=self.conn)

        return temp_card

    def select_salty_card(self):
        weighted_list = {}
        for name, card in self.related_cards.items():
            weighted_list[name] = card['salt']
        choice = random.choices(list(weighted_list.keys()), list(weighted_list.values()))
        choice = choice[0]
        temp_card = mtgcard(self.related_cards[choice]['url'], conn=self.conn)
        return temp_card


class mtgdeck:
    def __init__(self, commander, conn=None):
        self.commander = commander
        self.conn = conn
        self.card_count = 1
        self.basic_land_dict = {}
        self.basic_land_lookup_dict = {
            'W': 'https://edhrec.com/cards/plains',
            'U': 'https://edhrec.com/cards/island',
            'B': 'https://edhrec.com/cards/swamp',
            'G': 'https://edhrec.com/cards/forest',
            'R': 'https://edhrec.com/cards/mountain'
        }

        self.deck_list = {1: {self.commander.name: commander}}
    
    def mana_match(self, temp_card):
        if not temp_card.color_id:
            return True
        for color in temp_card.color_id:
            if color not in self.commander.color_id:
                return False
        return True

    def is_card_in_deck(self, temp_card):
        for dictionary in self.deck_list.values():
            if temp_card.name in dictionary.keys():
                return True
        return False

    def add_card(self, temp_card, relatedness):
        if self.mana_match(temp_card) == True:
            if self.is_card_in_deck(temp_card) != True:
                print('Adding', temp_card.name)
                if temp_card.type == 'Land':
                    if 'Basic Land' in temp_card.detail_type:
                        if temp_card.name in self.basic_land_dict.keys():
                            self.basic_land_dict[temp_card.name] += 1
                            return True
                        elif temp_card.name not in self.basic_land_dict.keys():
                            self.basic_land_dict[temp_card.name] = 1
                            return True
                        else:
                            return False
                if relatedness not in self.deck_list.keys():
                    self.deck_list[relatedness] = {}
                self.deck_list[relatedness][temp_card.name] = temp_card 
                return True
        return False

    def add_synergistic_card(self, type_list=['Creature', 'Sorcery', 'Instant', 'Enchantment', 'Artifact', 'Planeswalker', 'Land']):
        weighted_list = list(self.deck_list.keys())
        weighted_list.sort(reverse=True)
        added_card = False
        while added_card != True:
            stack_choice = random.choices(list(self.deck_list.keys()), weighted_list)[0]
            stack = list(self.deck_list[stack_choice].values())
            seed_card = random.choice(stack)
            temp_card = seed_card.select_synergistic_card(type_list=type_list)
            added_card = self.add_card(temp_card, stack_choice + 1)
        return added_card

    def calculate_mana_distribution(self):
        mana_dict = {}
        for dictionary in self.deck_list.values():
            for temp_card in dictionary.values():
                for color in temp_card.color_id:
                    if color in mana_dict.keys():
                        mana_dict[color] += 1
                    elif color not in mana_dict.keys():
                        mana_dict[color] = 1
        total_mana = sum(mana_dict.values())
        mana_distribution_dict = {}
        for color in mana_dict.keys():
            mana_distribution_dict[color] = mana_dict[color] / total_mana
        return mana_distribution_dict

    def add_basic_lands(self, color, number=1):
        card_url = self.basic_land_lookup_dict[color]
        temp_card = mtgcard(card_url, conn=self.conn)
        temp = self.add_card(temp_card, -1)
        return temp
    
    def count_cards(self, type_list=None):
        card_count = 0

        if type_list == None:
            for dictionary in self.deck_list.values():
                card_count += len(dictionary.keys())
            for value in self.basic_land_dict.values():
                card_count += value

        elif type_list:
            for dictionary in self.deck_list.values():
                for card in dictionary.values():
                    if card.type in type_list:
                        card_count += 1

            for value in self.basic_land_dict.values():
                card_count += value
        return card_count

    def calculate_average_mana(self):
        mana_list = []
        for dictionary in self.deck_list.values():
            for temp_card in dictionary.values():
                mana_list.append(temp_card.target_mana)
        self.land_target = int(sum(mana_list) / len(mana_list))
        return self.land_target

    def landfall(self):
        if not self.commander.color_id:
            current_lands = self.count_cards('Land')
            target_lands = self.land_target - current_lands
            if target_lands < 0:
                return True
            for x in range(target_lands):
                self.add_synergistic_card(['Land'])
            return self.count_cards('Land')

        current_lands = self.count_cards('Land')
        if current_lands > self.land_target:
            return False
        target_lands = self.land_target - current_lands
        if target_lands < 0:
            return True
        mana_distribution = self.calculate_mana_distribution()
        for color, value in mana_distribution.items():
            number_of_lands = value * target_lands
            number_of_lands = math.ceil(number_of_lands)
            print(number_of_lands)
            for x in range(number_of_lands):
                self.add_basic_lands(color=color)
        
        current_lands = self.count_cards('Land')
        if current_lands == self.land_target:
            return current_lands
        elif current_lands < self.land_target:
            while current_lands < self.land_target:
                self.add_synergistic_card(['Land'])
                current_lands = self.count_cards('Land')
            return current_lands
        elif current_lands > self.land_target:
            self.land_target = current_lands
            return current_lands
        else:
            return current_lands

    def print_deck_list(self):
        print_deck_list = []
        for dictionary in self.deck_list.values():
                for card in dictionary.values():
                    print_deck_list.append(card.name + ' x1')
        for color, value in self.basic_land_dict.items():
            print_deck_list.append(color + 'x' + value)
        return print_deck_list
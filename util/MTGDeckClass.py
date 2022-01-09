from itertools import combinations_with_replacement
from util import MTGCardClass
import requests
import json
import random
from datetime import datetime
import math

class MTGDeckClass:
    def __init__(self, seed_card, db_info=None):
        self.seed_card = seed_card
        self.commander = None
        self.db_info = db_info
        self.card_count = 0
        self.basic_land_dict = {}
        self.basic_land_lookup_dict = {
            'W': 'https://edhrec.com/cards/plains',
            'U': 'https://edhrec.com/cards/island',
            'B': 'https://edhrec.com/cards/swamp',
            'G': 'https://edhrec.com/cards/forest',
            'R': 'https://edhrec.com/cards/mountain'
        }
        self.land_target = 0
        self.select_commander()
    
    def select_commander(self):
        if self.seed_card.legal_commander == True:
            self.commander = self.seed_card
            self.deck_list = {1: {self.commander.name: self.commander}}
            self.card_count = self.count_cards()
        else:
            for dictionary in self.seed_card.json['cardlists']:
                if dictionary['header'] == 'Top Commanders':
                    commander_url = (random.choice(dictionary['cardviews']))['url']
                    self.commander = MTGCardClass.MTGCardClass(commander_url, self.db_info)
                    self.deck_list = {1: {self.commander.name: self.commander}}
                    self.deck_list = {2: {self.seed_card.name: self.seed_card}}
                    self.card_count = self.count_cards()
        print('Commander is', self.commander.name)
        return

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
        temp_card = MTGCardClass.MTGCardClass(card_url, self.db_info)
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
                mana_list.append(temp_card.cmc)
        self.land_target = int((sum(mana_list) / len(mana_list)) * 16.5) # 15 this is a constant based on looking at average number of lands per deck vs average mana cost in a deck
        if self.land_target > 40:
            self.land_target = 40
        if self.land_target < 35:
            self.land_target = 35        
        return self.land_target

    def landfall(self):
        self.calculate_average_mana()
        current_land_count = self.count_cards('Land')
        if current_land_count >= self.land_target:
            return

        if not self.commander.color_id: # For Colorless Commanders
            current_lands = self.count_cards('Land')
            target_lands = self.land_target - current_lands
            if target_lands < 0:
                return True
            for x in range(target_lands):
                self.add_synergistic_card(['Land'])
            return self.count_cards('Land')
        
        target_lands = self.land_target - current_land_count

        mana_distribution = self.calculate_mana_distribution()
        for color, value in mana_distribution.items():
            number_of_lands = value * target_lands
            number_of_lands = math.floor(number_of_lands)
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
            print_deck_list.append(color + ' x' + str(value))
        return print_deck_list
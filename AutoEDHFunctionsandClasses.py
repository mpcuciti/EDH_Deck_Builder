import requests
import json
import random
from datetime import datetime

# content = requests.get("https://edhrec-json.s3.amazonaws.com/en/cards/swords-to-plowshares.json")
# content = content.json()
# pprint.pprint(type(content['container']['json_dict']['cardlists'][5]['cardviews'][0]))

class mtgcard:
    def __init__(self, url, commander=False, conn=None):
        self.url = url
        self.conn = conn
        if commander == False:
            self.commander = False
        elif commander == True:
            self.commander = True
        else:
            commander == False

        self.clean_url()
        self.get_json(self.url)

    def clean_url(self):
        if self.url[0] == '/':
            self.short_url = self.url
            self.url = 'https://edhrec.com' + self.url

        if 'cards' in self.url:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/cards/'
        elif 'commanders' in self.url:
            url_base = 'https://edhrec-json.s3.amazonaws.com/en/commanders/'
        i = 0
        for each in self.url:
            if each == '/':
                output = i
            i += 1
        self.json_url = url_base + self.url[output + 1: len(self.url)] + '.json'
        return

    def check_if_card_in_database(self):
        if self.conn == None:
            self.raw_json = requests.get(self.json_url).json()
            return
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mtgcard_data WHERE url = %s",
            [self.json_url]
        )
        rows = cursor.fetchall()
        cursor.close()
        if not rows:
            self.add_json_to_db()
            return 'This is a test and nothing was returned'
        elif rows:
            self.load_json_from_db()
            return 'This is a test and something was retrieved'

    def add_json_to_db(self):
        temp = requests.get(self.json_url).text
        self.name = json.loads(temp)['container']['json_dict']['card']['name']
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO mtgcard_data (name, url, json_data, timestamp) VALUES(%s, %s, %s, %s) ;",
            [self.name, self.json_url, temp, datetime.now()]
        )
        self.conn.commit()
        cursor.close()
        self.load_json_from_db()
        return

    def load_json_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT json_data FROM mtgcard_data WHERE url = %s ;",
            [self.json_url]
            )
        row = cursor.fetchall()
        cursor.close()
        self.raw_json = dict(row[0][0])
        return

    def get_json(self, url):
        self.check_if_card_in_database()

        content = self.raw_json['container']['json_dict']
        self.raw_dict = content
        self.cmc = int(content['card']['cmc'])
        self.type = content['card']['type']
        self.name = content['card']['name']

        if 'legal_commander' in content['card']:
            self.legal_commander = content['card']['legal_commander']
        else:
            self.legal_commander = False


        if not content['card']['color_identity']:
            self.color_id = None
        self.color_id = content['card']['color_identity']

        if 'cardlists' in content.keys():
            self.card_lists = content['cardlists']
        else:
            self.card_lists = None

        self.top_commanders = self.search_card_lists('Top Commanders')
        self.top_cards = self.search_card_lists('Top Cards')
        self.top_synergy = self.search_card_lists('High Synergy Cards')        
        self.build_synergy_list()
        self.build_salt_list()

        self.short_url = '/cards/' + content['card']['sanitized']

    def build_synergy_list(self):
        self.synergy_list = None
        if self.card_lists:
            self.synergy_list = {}
            for dict in self.card_lists:
                if 'land' not in dict['header']:
                    for card in dict['cardviews']:
                        if 'synergy' in card.keys():
                            self.synergy_list[card['synergy']] = card['url'] 

    def build_salt_list(self):
        self.salt_list = None
        if self.card_lists:
            self.salt_list = {}
            for dict in self.card_lists:
                if 'land' not in dict['header']:
                    for card in dict['cardviews']:
                        self.synergy_list[card['salt']] = card['url'] 

    def search_card_lists(self, list_name):
        if self.card_lists == None:
            return None
        for dict in self.card_lists:
            if dict['header'] == list_name:
                return dict['cardviews']
        return None

##########################################
class mtgdeck:
    def __init__(self, commander, conn=None):
        self.commander = commander
        self.conn = conn
        self.deck_list = {self.commander.name: commander}
        self.mana_curve = {}
        self.land_target = random.randint(35, 42)
        self.seed_pile = None
        self.choice_list = []

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
        return False
    
    def add_top_commander_cards(self, x):
        index = 0
        number_of_cards_added = 0
        while number_of_cards_added < x and index < len(self.commander.top_cards):
            temp_card = mtgcard(self.commander.top_cards[index]['url'])
            if self.add_card(temp_card) == True:
                number_of_cards_added += 1
            index += 1     
        return number_of_cards_added

    def add_top_synergy_commander_cards(self, x):
        index = 0
        number_of_cards_added = 0
        while number_of_cards_added < x and index < len(self.commander.top_synergy):
            temp_card = mtgcard(self.commander.top_synergy[index]['url'])
            if self.add_card(temp_card) == True:
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

    def calculate_mana_distribution(self):
        self.mana_distribution = {}
        for card in self.deck_list.values():
            for color in card.color_id:
                if color not in self.mana_distribution.keys():
                    self.mana_distribution[color] = 1
                else:
                    self.mana_distribution[color] += 1
        self.calculate_deck_cmc()
        total_count = 0
        for count in self.mana_distribution.values():
            total_count += count
        for color, value in self.mana_distribution.items():
            self.mana_distribution[color] = value / total_count
        return

    def build_card_seed_pile(self):
        self.seed_pile = {}
        for card in self.deck_list.values():
            if card.synergy_list:
                for synergy, url in card.synergy_list.items():
                    if url not in self.seed_pile.values():
                        self.seed_pile[synergy] = url
        return

    def add_1_random_card_from_seed_pile(self):
        added_card = False
        while added_card != True:
            choice = random.choices(list(self.seed_pile.keys()), list(self.seed_pile.keys()), k=1)
            choice = choice[0]
            temp_card_url = self.seed_pile[choice]
            temp_card = mtgcard(temp_card_url, conn=self.conn)
            print('Trying to add', temp_card.name)

            added_card = self.add_card(temp_card)
            if added_card != True:
                self.seed_pile.pop(choice)
            if not self.seed_pile:
                return 'no cards left!'
        return
    
    def get_to_x_nonland_cards_in_deck(self,x):
        if not self.seed_pile:
            self.build_card_seed_pile()
    
        self.count_lands_in_deck()

        while x > (len(self.deck_list) - self.land_count):
            if len(self.seed_pile) < 10: 
                self.build_card_seed_pile()

            deck_size = len(self.deck_list.keys())
            self.add_1_random_card_from_seed_pile()
            if deck_size == len(self.deck_list.keys()):
                return 'Error: Ran out of seeds. No valid choices remaining'
            self.build_card_seed_pile()
            self.count_lands_in_deck()
        return

    def count_lands_in_deck(self):
        self.land_count = 0
        for card in self.deck_list.values():
            if 'land' in card.type:
                self.land_count += 1

    def calculate_deck_cmc(self):
        self.deck_cmc = 0
        for card in self.deck_list.values():
            self.deck_cmc += card.cmc

    def landfall(self):
        basic_land_dict = {
            'W': 'https://edhrec.com/cards/plains',
            'U': 'https://edhrec.com/cards/island',
            'B': 'https://edhrec.com/cards/swamp',
            'G': 'https://edhrec.com/cards/forest',
            'R': 'https://edhrec.com/cards/mountain'
        }
        self.calculate_mana_distribution()
        for color, value in self.mana_distribution.items():
            for x in range(int(value * float(self.land_target))):
                self.add_card(mtgcard(basic_land_dict[color]))


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

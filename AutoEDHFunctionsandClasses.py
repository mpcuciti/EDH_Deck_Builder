import requests
import json
import random
from datetime import datetime


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
        self.type = content['card']['type']
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
                        'type': card['type'], 
                        'color_id': card['color_identity'], 
                        'salt': card['salt'] 
                        }
        self.related_cards = url_dict





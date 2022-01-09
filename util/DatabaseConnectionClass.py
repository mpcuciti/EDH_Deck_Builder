    
def check_if_card_in_database(self):
    response = self.dynamodb.get_item(
        Key={
            'card_json_url': self.json_url
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        if 'Item' in response.keys():
            return True
        elif 'Item' not in response.keys():
            return False
        else:
            return False
    else:
        return False

def get_card_data(self):
    if self.check_if_card_in_database() == False:
        self.add_card_json_to_db()
    self.load_card_json_from_db()
    return

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
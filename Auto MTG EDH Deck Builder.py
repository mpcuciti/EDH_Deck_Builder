from random import seed
from AutoEDHFunctionsandClasses import *
from pprint import pprint
import psycopg2

#Here there be PsuedoCode
# 1. Is the given card a valid commander?
# 1a. If No, select the top commander from the json and assign that card object to the 'commander' variable
# 1b. If Yes, ask if that is the desired commander. If no, assign it to the card list and and perform step 1a.
# 3. Add the top 15 cards from the commanders top cards to the card list
# 4. Determine the mana curve (thus far) and estimate number of lands needed for a viable build. Provide this as a choice to the user
# 5. The total size of the desired deck list 100 less 15 top cards less 1 commander less the number of lands (lands also need to be proportional based on color identity)
# 6. 

#yes my DB credentials are in here
# no it's not permanent (just for testing)
# dont worry about it
conn = psycopg2.connect(
    host="postgresql.cuciti.net",
    database="mtgcard_db",
    user="mtgcard_db_user",
    password="jVvWcapRwg5j74"
)

seed_card_url = input('whats the edhrec url of your seed card?')
seed_card = mtgcard(seed_card_url, conn)
print('Seed Card is', seed_card.name)

if seed_card.legal_commander == True:
    print('Commander is', seed_card.name)
    deck = mtgdeck(seed_card, conn=conn)
elif seed_card.legal_commander != True:
    for card in seed_card.related_cards.values():
        temp_card = mtgcard(card['url'], conn)
        if temp_card.legal_commander == True:
            print('Commander is', temp_card.name)
            deck = mtgdeck(seed_card, conn=conn)

deck.calculate_average_mana()
for x in range (100 - deck.land_target):
    deck.add_synergistic_card()
deck.calculate_average_mana()
deck.landfall()
for x in range (100 - deck.count_cards()):
    deck.add_synergistic_card(['Creature', 'Sorcery', 'Instant', 'Enchantment', 'Artifact', 'Planeswalker'])
pprint(deck.print_deck_list())
from AutoEDHFunctionsandClasses import * 
from pprint import pprint

#Here there be PsuedoCode
# 1. Is the given card a valid commander?
# 1a. If No, select the top commander from the json and assign that card object to the 'commander' variable
# 1b. If Yes, ask if that is the desired commander. If no, assign it to the card list and and perform step 1a.
# 3. Add the top 15 cards from the commanders top cards to the card list
# 4. Determine the mana curve (thus far) and estimate number of lands needed for a viable build. Provide this as a choice to the user
# 5. The total size of the desired deck list 100 less 15 top cards less 1 commander less the number of lands (lands also need to be proportional based on color identity)
# 6. 

# there will eventually be a prompt here
seed_card_url = 'https://edhrec.com/cards/sen-triplets'
#seed_card_url = 'https://edhrec.com/cards/izzet-signet'
seed_card = mtgcard(seed_card_url)
print('Seed Card is', seed_card.name)

if seed_card.legal_commander == True:
    print(seed_card.name, 'is a legal commander')
    yesno = None
    index = 0
    while yesno != 'y':
        if yesno == None:
            yesno = input('Do you want this card to be your commander? (y/n) ')
            if yesno == 'y':
                    commander = mtgcard(seed_card.url, commander=True)
        elif yesno == 'n':
            if index < len(seed_card.top_commanders):
                temp_card = mtgcard(seed_card.top_commanders[index]['url'])
                pprint(temp_card.name)
                yesno = input('Do you want this card to be your commander? (y/n) ')
                if yesno == 'y':
                    commander = mtgcard(temp_card.url, commander=True)
                index += 1
            elif index >= len(seed_card.top_commanders):
                yesno = 'y'
                print('No Legal Commanders Remaining')
        else:
            print('Invalid Input')
else:
    print(seed_card.name, 'is not a legal commander')
    yesno = 'n'
    index = 0
    while yesno != 'y':
        if yesno == 'n':
            if index < len(seed_card.top_commanders):
                temp_card = mtgcard(seed_card.top_commanders[index]['url'])
                pprint(temp_card.name)
                yesno = input('Do you want this card to be your commander? (y/n) ')
                if yesno == 'y':
                    commander = temp_card
                index += 1
            elif index >= len(seed_card.top_commanders):
                yesno = 'y'
                print('No Legal Commanders Remaining')
        else:
            print('Invalid Input')

deck = mtgdeck(commander)
deck.add_top_commander_cards(3)

pprint(deck.deck_list.keys())
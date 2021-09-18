from AutoEDHFunctionsandClasses import * 

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

if is_valid_commander(seed_card_url) == True:
    print(seed_card_url)
    yesno1 = input('Do you want this card to be your commander? (y/n) ')
    if yesno1 == 'y':
        commander = mtgcard(seed_card_url)
    elif yesno1 == 'n':
        temp_card = mtgcard(seed_card_url)
        index = 0
        while index < len(temp_card.top_commanders):
            commander = None
            print(temp_card.top_commanders[index]['name'])
            yesno2 = input('Do you want this to be your commander? (y/n) ')
            if yesno2 == 'y':
                commander = mtgcard(temp_card.top_commanders[index]['url'])
                break
            elif yesno2 == 'n':
                index += 1
            else:
                print('invalid input')
elif is_valid_commander(seed_card_url) == False:
    print('Getting top commander based on card....')
    temp_card = mtgcard(seed_card_url)
    commander = mtgcard(temp_card.top_commanders[0]['url'])

card_list = list()
for i in commander.top_cards:
    print(i['name'])
    card_list.append(mtgcard(i['url']))

print(len(card_list))

for i in card_list:
    print(i.name)

        
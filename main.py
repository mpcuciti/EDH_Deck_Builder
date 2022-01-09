from util import MTGDeckClass, MTGCardClass, DatabaseConnectionClass

def main(seed_card_url = None):
    if seed_card_url == None:
        seed_card_url = input('whats the edhrec url of your seed card?')
    seed_card = MTGCardClass.MTGCardClass(seed_card_url, None)
    print('Seed Card is', seed_card.name)
    deck = MTGDeckClass.MTGDeckClass(seed_card, None)

    for x in range (50):
        deck.add_synergistic_card()
    deck.landfall()
    for x in range (100 - deck.count_cards()):
        deck.add_synergistic_card(['Creature', 'Sorcery', 'Instant', 'Enchantment', 'Artifact', 'Planeswalker'])
    return deck

main('https://edhrec.com/cards/mana-crypt')
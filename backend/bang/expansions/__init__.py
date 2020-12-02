
from bang.expansions.dodge_city import cards, characters
class DodgeCity():
    def get_characters():
        return characters.all_characters()
    def get_cards():
        return cards.get_starting_deck()

class DodgeCity():
    def get_characters():
        from bang.expansions.dodge_city import characters
        return characters.all_characters()

    def get_cards():
        from bang.expansions.dodge_city import cards
        return cards.get_starting_deck()

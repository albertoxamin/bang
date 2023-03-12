# pylint: skip-file

class DodgeCity():
    def get_characters():
        from bang.expansions.dodge_city import characters
        return characters.all_characters()

    def get_cards():
        from bang.expansions.dodge_city import cards
        return cards.get_starting_deck()

class GoldRush():
    def get_characters():
        from bang.expansions.gold_rush import characters
        return characters.all_characters()

class TheValleyOfShadows():
    def get_characters():
        from bang.expansions.the_valley_of_shadows import characters
        return characters.all_characters()

    def get_cards():
        from bang.expansions.the_valley_of_shadows import cards
        return cards.get_starting_deck()

class WildWestShow():
    def get_characters():
        from bang.expansions.wild_west_show import characters
        return characters.all_characters()
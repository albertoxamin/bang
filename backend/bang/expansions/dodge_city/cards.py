from bang.cards import *

class Riparo(Mustang):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Riparo'
        self.icon = '⛰'

def get_starting_deck() -> List[Card]:
    return [
        Riparo(Suit.DIAMONDS, 'K'),
        Mustang(Suit.DIAMONDS, 'K'),
    ]*100

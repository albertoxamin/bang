from bang.cards import *

class Riparo(Mustang):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Riparo'
        self.icon = '⛰'

class Binocolo(Mirino):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Binocolo'
        self.icon = '🔍'

class Pugno(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Pugno!', number, range=1)
        self.icon = '👊'
        self.desc = "Spara a un giocatore a distanta 1"
        self.need_target = True

    def play_card(self, player, against):
        if against != None:
            import bang.characters as chars
            super().play_card(player, against=against)
            player.game.attack(player, against)
            return True
        return False

def get_starting_deck() -> List[Card]:
    return [
        #TODO: aggiungere anche le carte normalmente presenti https://bang.dvgiochi.com/cardslist.php?id=3
        Riparo(Suit.DIAMONDS, 'K'),
        Binocolo(Suit.DIAMONDS, 10),
        Pugno(Suit.SPADES, 10),
    ]

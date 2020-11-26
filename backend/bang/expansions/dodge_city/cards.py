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
        Barile(Suit.CLUBS, 'A'),
        Binocolo(Suit.DIAMONDS, 10),
        Dinamite(Suit.CLUBS, 10),
        Mustang(Suit.HEARTS, 5),
        Remington(Suit.DIAMONDS, 6),
        RevCarabine(Suit.SPADES, 5),
        Riparo(Suit.DIAMONDS, 'K'),
        Bang(Suit.SPADES, 8),
        Bang(Suit.CLUBS, 5),
        Bang(Suit.CLUBS, 6),
        Bang(Suit.CLUBS, 'K'),
        Birra(Suit.HEARTS, 6),
        Birra(Suit.SPADES, 6),
        CatBalou(Suit.CLUBS, 8),
        Emporio(Suit.SPADES, 'A'),
        Indiani(Suit.DIAMONDS, 5),
        Mancato(Suit.DIAMONDS, 8),
        Panico(Suit.HEARTS, 'J'),
        Pugno(Suit.SPADES, 10),
    ]

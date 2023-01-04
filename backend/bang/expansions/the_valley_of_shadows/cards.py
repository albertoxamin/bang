from typing import List
from bang.cards import Card, Suit

class Fantasma(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Fantasma', number, is_equipment=True)
        self.icon = '👻️' #porta in vita i giocatori morti ma non 
        #TODO

class Lemat(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Lemat', number, is_equipment=True, is_weapon=True, range=1)
        self.icon = '🔫' # ogni carta può essere usata come bang
        #TODO

class SerpenteASonagli(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'SerpenteASonagli', number, is_equipment=True)
        self.need_target = True
        self.icon = '🐍️' # Ogni turno pesca se il seme picche -1hp
        self.alt_text = "♠️=💔"
        #TODO

class Shotgun(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Shotgun', number, is_equipment=True, range=1)
        self.icon = '🔫' # Ogni volta che colpisci un giocatore deve scartare una carta
        #TODO

class Taglia(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Taglia', number, is_equipment=True)
        self.need_target = True
        self.icon = '💰' # chiunque colpisca il giocatore con la taglia pesca una carta dal mazzo, si toglie solo con panico, cat balou, dalton
        #TODO

class UltimoGiro(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'UltimoGiro', number)
        self.icon = '🥂'
        # self.desc = 'Recupera 1 vita'
        # self.desc_eng = 'Regain 1 HP'
        self.alt_text = "🍺"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against)
        player.lives = min(player.lives+1, player.max_lives)
        player.notify_self()
        return True

class Tomahawk(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Tomahawk', number, range=2)
        self.icon = '🪓️'
        self.alt_text = "2🔎 💥"
        # "Spara a un giocatore a distanza 2"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            super().play_card(player, against=against)
            player.game.attack(player, against)
            return True
        return False

class Sventagliata(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Sventagliata', number)
        self.icon = '💕️'
        self.alt_text = "💥💥" # spara al target e anche, a uno a distanza 1 dal target
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            #TODO
            # super().play_card(player, against=against)
            # player.game.attack(player, against)
            return True
        return False

class Salvo(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Salvo', number)
        self.icon = '😇️'
        self.alt_text = "👤😇️" 
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            #TODO
            # super().play_card(player, against=against)
            # player.game.attack(player, against)
            return True
        return False

def get_starting_deck() -> List[Card]:
    cards = [
        Fantasma(Suit.SPADES, 9),
        Fantasma(Suit.SPADES, 10),
        Lemat(Suit.DIAMONDS, 4),
        SerpenteASonagli(Suit.HEARTS, 7),
        Shotgun(Suit.SPADES, 'K'),
        Taglia(Suit.CLUBS, 9),
        UltimoGiro(Suit.DIAMONDS, 8),
        Tomahawk(Suit.DIAMONDS, 'A'),
        Sventagliata(Suit.SPADES, 2),
        Salvo(Suit.HEARTS, 5),
        # Bandidos(Suit.DIAMONDS,'Q'), # gli altri  giocatori scelgono se scartare 2 carte o perdere 1 punto vita
        # Fuga(Suit.HEARTS, 3), # evita l'effetto di carte marroni (tipo panico cat balou) di cui sei bersaglio
        # Mira(Suit.CLUBS, 6), # gioca questa con una carta bang, per fare -2hp
        # Poker(Suit.HEARTS, 'J'), # tutti gli altri scartano 1 carta a scelta, se non ci sono assi allora pesca 2 dal mazzo
        # RitornoDiFiamma(Suit.CLUBS, 'Q'), # un mancato che fa bang
    ]
    for c in cards:
        c.expansion_icon = '👻️'
    return cards

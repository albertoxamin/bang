from bang.cards import *

class ShopCardKind(IntEnum):
    BROWN = 0  # Se l’equipaggiamento ha il bordo marrone, applicane subito l’effetto e poi scartalo.
    BLACK = 1  # Se l’equipaggiamento ha il bordo nero, tienilo scoperto di fronte a te.

class ShopCard(Card):
    def __init__(self, name:str, cost:int, kind:ShopCardKind):
        super().__init__(suit='💵', number=cost, name=name)
        self.kind = kind

    def play_card(self, player, against, _with=None):
        if self.kind == ShopCardKind.BROWN:
            pass # use it now
            return False
        elif self.kind == ShopCardKind.BLACK: # equip it
            self.reset_card()
            if not self.is_duplicate_card(player):
                self.reset_card()
                player.equipment.append(self)
                return True
            else:
                return False

class Bicchierino(ShopCard):
    def __init__(self):
        super().__init__('Bicchierino', 1, ShopCardKind.BROWN)
        self.icon = '🍸️'

    def play_card(self, player, against, _with=None):
        if against != None:
            player.sio.emit('chat_message', room=player.game.name, data=f'_play_card_for|{player.name}|{self.name}|{against}')
            player.game.deck.scrap(_with)
            player.game.get_player_named(against).lives = min(player.game.get_player_named(against).lives+1, player.game.get_player_named(against).max_lives)
            player.game.get_player_named(against).notify_self()
            return True
        return False

class Bottiglia(ShopCard):
    def __init__(self):
        super().__init__('Bottiglia', 2, ShopCardKind.BROWN)
        self.icon = '🍾️'

    def play_card(self, player, against, _with=None):
        if against != None:
            pass # bang, birra, panico
        return False

class Complice(ShopCard):
    def __init__(self):
        super().__init__('Complice', 2, ShopCardKind.BROWN)
        self.icon = '😉️'

    def play_card(self, player, against, _with=None):
        if against != None:
            pass # emporio, duello, Cat balou
        return False

class CorsaAllOro(ShopCard):
    def __init__(self):
        super().__init__("Corsa All'Oro", 5, ShopCardKind.BROWN)
        self.icon = '🤑️'

    def play_card(self, player, against, _with=None):
        if against != None:
            pass # termini turno, vita max, poi inizi un nuovo turno
        return False

class Rum(ShopCard):
    def __init__(self):
        super().__init__("Rum", 3, ShopCardKind.BROWN)
        self.icon = '🍷️'

    def play_card(self, player, against, _with=None):
        if against != None:
            pass # Estrai 4 carte e ottieni 1 hp per ogni seme diverso
        return False

class UnionPacific(ShopCard):
    def __init__(self):
        super().__init__("Union Pacific", 4, ShopCardKind.BROWN)
        self.icon = '🚆️'

    def play_card(self, player, against, _with=None):
        if against != None:
            pass # Pesca 4 carte
        return False

class Calumet(ShopCard):
    def __init__(self):
        super().__init__("Calumet", 3, ShopCardKind.BLACK)
        self.icon = '🚭️'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # ti rende immuni ai quadri

class Cinturone(ShopCard):
    def __init__(self):
        super().__init__("Cinturone", 2, ShopCardKind.BLACK)
        self.icon = '🥡'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # max carte a fine turno 8

class FerroDiCavallo(ShopCard):
    def __init__(self):
        super().__init__("Ferro di Cavallo", 2, ShopCardKind.BLACK)
        self.icon = '🎠'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # estrai come luky duke

class Piccone(ShopCard):
    def __init__(self):
        super().__init__("Piccone", 4, ShopCardKind.BLACK)
        self.icon = '⛏️'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # peschi una carta in piu a inizio turno

class Ricercato(ShopCard):
    def __init__(self):
        super().__init__("Ricercato", 2, ShopCardKind.BLACK)
        self.icon = '🤠️'

    def play_card(self, player, against, _with=None):
        pass
        # la giochi su un altro giocatore, ricompensa di 2 carte e 1 pepita a chi lo uccide

class Setaccio(ShopCard):
    def __init__(self):
        super().__init__("Setaccio", 3, ShopCardKind.BLACK)
        self.icon = '🥘️'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # paghi 1 pepita per pescare 1 carta durante il tuo turno (max 2 volte per turno)

class Stivali(ShopCard):
    def __init__(self):
        super().__init__("Stivali", 3, ShopCardKind.BLACK)
        self.icon = '🥾️'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # peschi una carta ogni volta che vieni ferito

class Talismano(ShopCard):
    def __init__(self):
        super().__init__("Talismano", 3, ShopCardKind.BLACK)
        self.icon = '🧿'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # ottieni una pepita ogni volta che vieni ferito

class Zaino(ShopCard):
    def __init__(self):
        super().__init__("Zaino", 3, ShopCardKind.BLACK)
        self.icon = '🎒️'

    def play_card(self, player, against, _with=None):
        super().play_card(player, against, _with)
        # paga 2 pepite per recuperare 1 vita

def get_cards() -> List[Card]:
    cards = [
        Bicchierino(),
        Bottiglia(),
        Complice(),
        CorsaAllOro(),
        Rum(),
        UnionPacific(),
        Calumet(),
        Cinturone(),
        FerroDiCavallo(),
        Piccone(),
        Ricercato(),
        Setaccio(),
        Stivali(),
        Talismano(),
        Zaino(),
    ]
    for c in cards:
        c.expansion_icon = '🤑️'
    return cards

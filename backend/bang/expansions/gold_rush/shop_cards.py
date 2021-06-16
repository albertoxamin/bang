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
                self.can_be_used_now = True
                player.gold_rush_equipment.append(self)
                return True
            else:
                return False

    def reset_card(self):
        if self.kind == ShopCardKind.BLACK:
            self.can_be_used_now = False

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

    def play_card(self, player, against=None, _with=None):
        player.lives = player.max_lives
        return True

class Rum(ShopCard):
    def __init__(self):
        super().__init__("Rum", 3, ShopCardKind.BROWN)
        self.icon = '🍷️'

    def play_card(self, player, against=None, _with=None):
        # Estrai 4 carte e ottieni 1 hp per ogni seme diverso
        player.lives = min(player.lives+len({player.game.deck.pick_and_scrap().suit for i in range(4)}), player.max_lives)
        return True

class UnionPacific(ShopCard):
    def __init__(self):
        super().__init__("Union Pacific", 4, ShopCardKind.BROWN)
        self.icon = '🚆️'

    def play_card(self, player, against=None, _with=None):
        player.sio.emit('chat_message', room=player.game.name,
                        data=f'_UnionPacific|{player.name}|{self.name}')
        for i in range(4):
            player.hand.append(player.game.deck.draw())
        return True

class Calumet(ShopCard):
    def __init__(self):
        super().__init__("Calumet", 3, ShopCardKind.BLACK)
        self.icon = '🚭️'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        # ti rende immuni ai quadri

class Cinturone(ShopCard):
    def __init__(self):
        super().__init__("Cinturone", 2, ShopCardKind.BLACK)
        self.icon = '🥡'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        # max carte a fine turno 8

class FerroDiCavallo(ShopCard):
    def __init__(self):
        super().__init__("Ferro di Cavallo", 2, ShopCardKind.BLACK)
        self.icon = '🎠'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        # estrai come luky duke

class Piccone(ShopCard):
    def __init__(self):
        super().__init__("Piccone", 4, ShopCardKind.BLACK)
        self.icon = '⛏️'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        # peschi una carta in piu a inizio turno

class Ricercato(ShopCard):
    def __init__(self):
        super().__init__("Ricercato", 2, ShopCardKind.BLACK)
        self.icon = '🤠️'

    def play_card(self, player, against=None, _with=None):
        pass
        # TODO
        # la giochi su un altro giocatore, ricompensa di 2 carte e 1 pepita a chi lo uccide

class Setaccio(ShopCard):
    def __init__(self):
        super().__init__("Setaccio", 3, ShopCardKind.BLACK)
        self.icon = '🥘️'

    def play_card(self, player, against=None, _with=None):
        if not self.can_be_used_now:
            super().play_card(player, against, _with)
        else:
            if player.gold_nuggets > 1:
                player.gold_nuggets -= 1
                player.hand.append(player.game.deck.draw())
        # paghi 1 pepita per pescare 1 carta durante il tuo turno (max 2 volte per turno)

class Stivali(ShopCard):
    def __init__(self):
        super().__init__("Stivali", 3, ShopCardKind.BLACK)
        self.icon = '🥾️'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        # peschi una carta ogni volta che vieni ferito

class Talismano(ShopCard):
    def __init__(self):
        super().__init__("Talismano", 3, ShopCardKind.BLACK)
        self.icon = '🧿'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        # ottieni una pepita ogni volta che vieni ferito

class Zaino(ShopCard):
    def __init__(self):
        super().__init__("Zaino", 3, ShopCardKind.BLACK)
        self.icon = '🎒️'

    def play_card(self, player, against=None, _with=None):
        super().play_card(player, against, _with)
        if not self.can_be_used_now:
            super().play_card(player, against, _with)
        else:
            if player.gold_nuggets > 2:
                player.gold_nuggets -= 2
                player.lives = min(player.lives + 1, player.max_lives)
        # paga 2 pepite per recuperare 1 vita

def get_cards() -> List[Card]:
    cards = [
        # Bicchierino(),
        # Bottiglia(),
        # Complice(),
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
        c.expansion = 'gold_rush'
    return cards

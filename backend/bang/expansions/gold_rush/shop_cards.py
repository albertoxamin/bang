from bang.cards import *
import bang.roles as r
import bang.players as pl
from globals import G, PendingAction

class ShopCardKind(IntEnum):
    BROWN = 0  # Se l’equipaggiamento ha il bordo marrone, applicane subito l’effetto e poi scartalo.
    BLACK = 1  # Se l’equipaggiamento ha il bordo nero, tienilo scoperto di fronte a te.

class ShopCard(Card):
    def __init__(self, name:str, cost:int, kind:ShopCardKind):
        super().__init__(suit='💵', number=cost, name=name)
        self.kind = kind
        self.expansion_icon = '🤑️'
        self.expansion = 'gold_rush'
        self.reset_card()

    def play_card(self, player, against, _with=None):
        if self.kind == ShopCardKind.BROWN:
            G.sio.emit('chat_message', room=player.game.name, data=f'_purchase_card|{player.name}|{self.name}')
            return True
        elif self.kind == ShopCardKind.BLACK: # equip it
            if not self.is_duplicate_card(player):
                self.reset_card()
                self.can_be_used_now = True
                player.gold_rush_equipment.append(self)
                G.sio.emit('chat_message', room=player.game.name, data=f'_purchase_card|{player.name}|{self.name}')
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

    def play_card(self, player, against=None, _with=None):
        player.available_cards = [{
            'name': p.name,
            'icon': p.role.icon if(player.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
            'alt_text': ''.join(['❤️']*p.lives)+''.join(['💀']*(p.max_lives-p.lives)),
            'is_character': True,
            'is_player': True
        } for p in player.game.get_alive_players()]
        player.choose_text = 'choose_bicchierino'
        player.pending_action = PendingAction.CHOOSE
        player.notify_self()
        return super().play_card(player, against, _with)

class Bottiglia(ShopCard):
    def __init__(self):
        super().__init__('Bottiglia', 2, ShopCardKind.BROWN)
        self.icon = '🍾️'

    def play_card(self, player, against=None, _with=None):
        # bang, birra, panico
        player.available_cards = [Bang(4,42), Birra(4,42), Panico(4,42)]
        if not any((player.get_sight() >= p['dist'] for p in player.game.get_visible_players(player))):
            player.available_cards.pop(0)
        for i in range(len(player.available_cards)):
            player.available_cards[i].must_be_used = True
        player.choose_text = 'choose_bottiglia'
        player.pending_action = PendingAction.CHOOSE
        player.notify_self()
        return super().play_card(player, against, _with)

class Complice(ShopCard):
    def __init__(self):
        super().__init__('Complice', 2, ShopCardKind.BROWN)
        self.icon = '😉️'

    def play_card(self, player, against=None, _with=None):
        # emporio, duello, Cat balou
        player.available_cards = [Emporio(4,42), Duello(4,42), CatBalou(4,42)]
        for i in range(len(player.available_cards)):
            player.available_cards[i].must_be_used = True
        player.choose_text = 'choose_complice'
        player.pending_action = PendingAction.CHOOSE
        player.notify_self()
        return super().play_card(player, against, _with)

class CorsaAllOro(ShopCard):
    def __init__(self):
        super().__init__("Corsa All Oro_gr", 5, ShopCardKind.BROWN)
        self.icon = '🤑️'

    def play_card(self, player, against=None, _with=None):
        player.lives = player.max_lives
        player.play_turn()
        return super().play_card(player, against, _with)

class Rum(ShopCard):
    def __init__(self):
        super().__init__("Rum", 3, ShopCardKind.BROWN)
        self.icon = '🍷️'

    def play_card(self, player, against=None, _with=None):
        # Estrai 4 carte e ottieni 1 hp per ogni seme diverso
        import bang.characters as c
        suits = set()
        num = 5 if player.character.check(player.game, c.LuckyDuke) else 4
        for i in range(num):
            c = player.game.deck.pick_and_scrap()
            G.sio.emit('chat_message', room=player.game.name, data=f'_flipped|{player.name}|{c.name}|{c.num_suit()}')
            suits.add(c.suit)
        player.lives = min(player.lives+len(suits), player.max_lives)
        return super().play_card(player, against, _with)

class UnionPacific(ShopCard):
    def __init__(self):
        super().__init__("Union Pacific", 4, ShopCardKind.BROWN)
        self.icon = '🚆️'

    def play_card(self, player, against=None, _with=None):
        G.sio.emit('chat_message', room=player.game.name,
                        data=f'_UnionPacific|{player.name}|{self.name}')
        for i in range(4):
            player.game.deck.draw(True, player=player)
        return super().play_card(player, against, _with)

class Calumet(ShopCard):
    def __init__(self):
        super().__init__("Calumet", 3, ShopCardKind.BLACK)
        self.icon = '🚭️'

    def play_card(self, player, against=None, _with=None):
        return super().play_card(player, against, _with)
        # ti rende immuni ai quadri

class Cinturone(ShopCard):
    def __init__(self):
        super().__init__("Cinturone", 2, ShopCardKind.BLACK)
        self.icon = '🥡'

    def play_card(self, player, against=None, _with=None):
        return super().play_card(player, against, _with)
        # max carte a fine turno 8

class FerroDiCavallo(ShopCard):
    def __init__(self):
        super().__init__("Ferro di Cavallo", 2, ShopCardKind.BLACK)
        self.icon = '🎠'

    def play_card(self, player, against=None, _with=None):
        return super().play_card(player, against, _with)
        # estrai come luky duke

class Piccone(ShopCard):
    def __init__(self):
        super().__init__("Piccone", 4, ShopCardKind.BLACK)
        self.icon = '⛏️'

    def play_card(self, player, against=None, _with=None):
        return super().play_card(player, against, _with)
        # peschi una carta in piu a inizio turno

class Ricercato(ShopCard):
    def __init__(self):
        super().__init__("Ricercato", 2, ShopCardKind.BLACK)
        self.icon = '🤠️'
        self.can_target_self = True

    def play_card(self, player, against=None, _with=None):
        G.sio.emit('chat_message', room=player.game.name, data=f'_purchase_card|{player.name}|{self.name}')
        player.available_cards = [{
            'name': p.name,
            'icon': p.role.icon if(player.game.initial_players == 3) else '🤠',
            'alt_text': ''.join(['❤️']*p.lives)+''.join(['💀']*(p.max_lives-p.lives)),
            'is_character': True,
            'is_player': True
        } for p in player.game.get_alive_players() if p != player and not isinstance(p.role, r.Sheriff)]
        player.available_cards.append({'name': player.name, 'number':0,'icon': 'you', 'is_character': True})
        player.choose_text = 'choose_ricercato'
        player.pending_action = PendingAction.CHOOSE
        player.notify_self()
        return True
        # la giochi su un altro giocatore, ricompensa di 2 carte e 1 pepita a chi lo uccide

class Setaccio(ShopCard):
    def __init__(self):
        super().__init__("Setaccio", 3, ShopCardKind.BLACK)
        self.icon = '🥘️'

    def play_card(self, player, against=None, _with=None):
        if not self.can_be_used_now:
            return super().play_card(player, against, _with)
        else:
            if player.gold_nuggets >= 1 and player.setaccio_count < 2:
                G.sio.emit('chat_message', room=player.game.name, data=f'_play_card|{player.name}|{self.name}')
                player.gold_nuggets -= 1
                player.setaccio_count += 1
                player.game.deck.draw(True, player=player)
                player.notify_self()
                return True
            return False
        # paghi 1 pepita per pescare 1 carta durante il tuo turno (max 2 volte per turno)

class Stivali(ShopCard):
    def __init__(self):
        super().__init__("Stivali", 3, ShopCardKind.BLACK)
        self.icon = '🥾️'

    def play_card(self, player, against=None, _with=None):
        return super().play_card(player, against, _with)
        # peschi una carta ogni volta che vieni ferito

class Talismano(ShopCard):
    def __init__(self):
        super().__init__("Talismano", 3, ShopCardKind.BLACK)
        self.icon = '🧿'

    def play_card(self, player, against=None, _with=None):
        return super().play_card(player, against, _with)
        # ottieni una pepita ogni volta che vieni ferito

class Zaino(ShopCard):
    def __init__(self):
        super().__init__("Zaino", 3, ShopCardKind.BLACK)
        self.icon = '🎒️'

    def play_card(self, player, against=None, _with=None):
        if not self.can_be_used_now:
            return super().play_card(player, against, _with)
        else:
            if player.gold_nuggets >= 2:
                G.sio.emit('chat_message', room=player.game.name, data=f'_play_card|{player.name}|{self.name}')
                player.gold_nuggets -= 2
                player.lives = min(player.lives + 1, player.max_lives)
                player.notify_self()
                return True
            return False
        # paga 2 pepite per recuperare 1 vita

def get_cards() -> List[Card]:
    cards = [
        Bicchierino(),
        Bicchierino(),
        Bicchierino(),
        Bottiglia(),
        Bottiglia(),
        Bottiglia(),
        Complice(),
        Complice(),
        Complice(),
        CorsaAllOro(),
        Rum(),
        Rum(),
        UnionPacific(),
        Calumet(),
        Cinturone(),
        FerroDiCavallo(),
        Piccone(),
        Ricercato(),
        Ricercato(),
        Ricercato(),
        Setaccio(),
        Stivali(),
        Talismano(),
        Zaino(),
    ]
    return cards

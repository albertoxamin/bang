from bang.cards import *

class Binocolo(Mirino):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Binocolo'
        self.icon = '🔍'

class Riparo(Mustang):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Riparo'
        self.icon = '⛰'

class Pugno(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Pugno!', number, range=1)
        self.icon = '👊'
        self.alt_text = "1🔎 💥"
        # self.desc = "Spara a un giocatore a distanza 1"
        # self.desc_eng = "Shoot a player at distance 1"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against != None:
            super().play_card(player, against=against)
            player.game.attack(player, against)
            return True
        return False

class Schivata(Mancato):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Schivata'
        self.icon = '🙅‍♂️'
        # self.desc += " e poi pesca una carta"
        # self.desc_eng += " and then draw a card."
        self.alt_text = "😅 | 🎴"

    def play_card(self, player, against, _with=None):
        return False

    def use_card(self, player):
        player.hand.append(player.game.deck.draw())
        player.notify_self()

class RagTime(Panico):
    def __init__(self, suit, number):
        Card.__init__(self, suit, 'Rag Time', number)
        self.icon = '🎹'
        # self.desc = "Ruba 1 carta da un giocatore a prescindere dalla distanza"
        # self.desc_eng = "Steal a card from another player at any distance"
        self.need_target = True
        self.need_with = True
        self.alt_text = '2🃏 | 👤😱'

    def play_card(self, player, against, _with):
        if against != None and _with != None:
            player.game.deck.scrap(_with)
            super().play_card(player, against=against)
            return True
        return False

class Rissa(CatBalou):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Rissa'
        self.icon = '🥊'
        # self.desc = "Fai scartare una carta a tutti gli altri giocatori, scegli a caso dalla mano, oppure fra quelle che hanno in gioco"
        # self.desc_eng = "Choose a card to discard from the hand/equipment of all the other players"
        self.need_with = True
        self.need_target = False
        self.alt_text = '2🃏 | 👤💃'

    def play_card(self, player, against, _with):
        if _with != None:
            players_with_cards = [p.name for p in player.game.players if p != player and (len(p.hand)+len(p.equipment)) > 0]
            if len(players_with_cards) == 0:
                return False
            player.game.deck.scrap(_with)
            player.event_type = 'rissa'
            super().play_card(player, against=players_with_cards[0])
            player.sio.emit('chat_message', room=player.game.name, data=f'_play_card|{player.name}|{self.name}')
            return True
        return False

class SpringField(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Springfield', number)
        self.icon = '🌵'
        # self.desc = "Spara a un giocatore a prescindere dalla distanza"
        # self.desc_eng = "Shoot a player at any distance"
        self.need_target = True
        self.need_with = True
        self.alt_text = '2🃏 | 👤💥'

    def play_card(self, player, against, _with=None):
        if against != None and _with != None:
            player.game.deck.scrap(_with)
            super().play_card(player, against=against)
            player.game.attack(player, against)
            return True
        return False

class Tequila(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Tequila', number)
        self.icon = '🍹'
        # self.desc = "Fai recuperare 1 vita a un giocatore a tua scelta, anche te stesso"
        # self.desc_eng = "Heal 1 HP to a player of your choice (can be you)"
        self.need_target = True
        self.can_target_self = True
        self.need_with = True
        self.alt_text = "2🃏 | 👤🍺"

    def play_card(self, player, against, _with=None):
        if against != None and _with != None:
            player.sio.emit('chat_message', room=player.game.name, data=f'_play_card_for|{player.name}|{self.name}|{against}')
            player.game.deck.scrap(_with)
            player.game.get_player_named(against).lives = min(player.game.get_player_named(against).lives+1, player.game.get_player_named(against).max_lives)
            player.game.get_player_named(against).notify_self()
            return True
        return False

class Whisky(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Whisky', number)
        self.icon = '🥃'
        # self.desc = "Gioca questa carta per recuperare fino a 2 punti vita"
        # self.desc_eng = "Heal 2 HP"
        self.need_with = True
        self.alt_text = '2🃏 | 🍺🍺'

    def play_card(self, player, against, _with=None):
        if _with != None:
            super().play_card(player, against=against)
            player.game.deck.scrap(_with)
            player.lives = min(player.lives+2, player.max_lives)
            player.notify_self()
            return True
        return False

class Bibbia(Schivata):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Bibbia'
        self.icon = '📖'
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            pass
            return False
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class Cappello(Mancato):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Cappello'
        self.icon = '🧢'
        self.usable_next_turn = True
        self.can_be_used_now = False
        self.alt_text = "😅"

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            pass
            return False
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class PlaccaDiFerro(Cappello):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Placca Di Ferro'
        self.icon = '🛡'

class Sombrero(Cappello):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Sombrero'
        self.icon = '👒'

class Pugnale(Pugno):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Pugnale'
        self.icon = '🗡'
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            return super().play_card(player, against=against)
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class Derringer(Pugnale):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Derringer'
        self.icon = '🚬'
        self.alt_text += ' 🎴'
        # self.desc += ' e poi pesca una carta'
        # self.desc_eng += ' and then draw a card.'

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            player.hand.append(player.game.deck.draw())
            return super().play_card(player, against=against)
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

    def use_card(self, player):
        player.hand.append(player.game.deck.draw())
        player.notify_self()

class Borraccia(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Borraccia', number)
        self.icon = '🍼'
        # self.desc = 'Recupera 1 vita'
        # self.desc_eng = 'Regain 1 HP'
        self.alt_text = "🍺"
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            super().play_card(player, against)
            player.lives = min(player.lives+1, player.max_lives)
            player.notify_self()
            return True
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class PonyExpress(WellsFargo):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Pony Express'
        self.icon = '🦄'
        self.alt_text = "🎴🎴🎴"
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            return super().play_card(player, against)
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class Howitzer(Gatling):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Howitzer'
        self.icon = '📡'
        self.alt_text = "👥💥"
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            return super().play_card(player, against)
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class CanCan(CatBalou):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = "Can Can"
        self.icon = "👯‍♀️"
        self.alt_text = "👤💃"
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            player.sio.emit('chat_message', room=player.game.name, data=f'_play_card_against|{player.name}|{self.name}|{against}')
            return super().play_card(player, against)
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class Conestoga(Panico):
    def __init__(self, suit, number):
        Card.__init__(self, suit, 'Conestoga', number)
        self.icon = "🏕"
        # self.desc = "Ruba 1 carta da un giocatore a prescindere dalla distanza"
        # self.desc_eng = "Steal a card from another player at any distance"
        self.alt_text = "👤😱"
        self.need_target = True
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            return super().play_card(player, against)
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class Pepperbox(Bang):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = 'Pepperbox'
        self.icon = '🌶'
        self.alt_text = "💥"
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            if against != None:
                Card.play_card(self, player, against=against)
                player.game.attack(player, against)
                return True
            return False
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

class FucileDaCaccia(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Fucile Da Caccia', number)
        self.icon = '🌂'
        # self.desc = "Spara a un giocatore a prescindere dalla distanza"
        self.alt_text = "👤💥"
        self.need_target = True
        self.usable_next_turn = True
        self.can_be_used_now = False

    def play_card(self, player, against, _with=None):
        if self.can_be_used_now:
            if against != None:
                super().play_card(player, against=against)
                player.game.attack(player, against)
                return True
            return False
        else:
            if not self.is_duplicate_card(player):
                player.equipment.append(self)
                return True
            else:
                return False

def get_starting_deck() -> List[Card]:
    cards = [
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
        RagTime(Suit.HEARTS, 9),
        Rissa(Suit.SPADES, 'J'),
        Schivata(Suit.DIAMONDS, 7),
        Schivata(Suit.HEARTS, 'K'),
        SpringField(Suit.SPADES, 'K'),
        Tequila(Suit.CLUBS, 9),
        Whisky(Suit.HEARTS, 'Q'),
        Bibbia(Suit.HEARTS, 10),
        Cappello(Suit.DIAMONDS, 'J'),
        PlaccaDiFerro(Suit.DIAMONDS, 'A'),
        PlaccaDiFerro(Suit.SPADES, 'Q'),
        Sombrero(Suit.CLUBS, 7),
        Pugnale(Suit.HEARTS, 8),
        Derringer(Suit.SPADES, 7),
        Borraccia(Suit.HEARTS, 7),
        CanCan(Suit.CLUBS, 'J'),
        Conestoga(Suit.DIAMONDS, 9),
        FucileDaCaccia(Suit.CLUBS, 'Q'),
        PonyExpress(Suit.DIAMONDS, 'Q'),
        Pepperbox(Suit.HEARTS, 'A'),
        Howitzer(Suit.SPADES, 9),
    ]
    for c in cards:
        c.expansion_icon = '🐄️'
    return cards

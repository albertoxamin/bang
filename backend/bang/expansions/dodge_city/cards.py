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
        self.desc = "Spara a un giocatore a distanta 1"
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
        self.desc += " e poi pesca una carta"

    def play_card(self, player, against, _with=None):
        return False

    def use_card(self, player):
        player.hand.append(player.game.deck.draw())
        player.notify_self()

class RagTime(Panico):
    def __init__(self, suit, number):
        Card.__init__(self, suit, 'Rag Time', number)
        self.icon = '🎹'
        self.desc = "Ruba 1 carta dalla mano di un giocatore"
        self.need_target = True
        self.need_with = True
        self.alt_text = '‼️'

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
        self.need_with = True
        self.need_target = False
        self.alt_text = '‼️'

    def play_card(self, player, against, _with):
        if _with != None:
            player.game.deck.scrap(_with)
            player.event_type = 'rissa'
            super().play_card(player, against=[p.name for p in player.game.players if p != player][0])
            return True
        return False

class SpringField(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Springfield', number)
        self.icon = '🌵'
        self.desc = "Spara a un giocatore"
        self.need_target = True
        self.need_with = True
        self.alt_text = '‼️'

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
        self.desc = "Fai recuperare 1 vita a un giocatore"
        self.need_target = True
        self.need_with = True
        self.alt_text = '‼️'

    def play_card(self, player, against, _with=None):
        if against != None and _with != None:
            player.game.deck.scrap(_with)
            player.game.get_player_named(against).lives = min(player.game.get_player_named(against).lives+1, player.game.get_player_named(against).max_lives)
            player.game.get_player_named(against).notify_self()
            return True
        return False

class Whisky(Card):
    def __init__(self, suit, number):
        super().__init__(suit, 'Whisky', number)
        self.icon = '🥃'
        self.desc = "Recupera 2 vite"
        self.need_with = True
        self.alt_text = '‼️'

    def play_card(self, player, against, _with=None):
        if _with != None:
            player.game.deck.scrap(_with)
            player.lives = min(player.lives+2, player.max_lives)
            player.notify_self()
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
        Schivata(Suit.DIAMONDS, 7),
        Schivata(Suit.HEARTS, 'K'),
        RagTime(Suit.HEARTS, 9),
        Rissa(Suit.SPADES, 'J'),
        SpringField(Suit.SPADES, 'K'),
        Tequila(Suit.CLUBS, 9),
        Whisky(Suit.HEARTS, 'Q'),
    ]

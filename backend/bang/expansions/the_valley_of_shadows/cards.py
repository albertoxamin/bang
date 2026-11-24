from typing import List
import bang.roles as r
import bang.players as pl
from bang.cards import Card, Suit, Bang, Mancato
import bang.expansions.fistful_of_cards.card_events as ce
from globals import G, PendingAction


class Fantasma(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Fantasma", number, is_equipment=True)
        self.icon = "👻️"  # porta in vita i giocatori morti ma non

    def play_card(self, player, against, _with=None):
        if (player.game.check_event(ce.IlGiudice)) or not self.can_be_used_now:
            return False
        if len(player.game.get_dead_players(include_ghosts=False)) > 0:
            player.pending_action = PendingAction.CHOOSE
            player.choose_text = "choose_fantasma"
            player.available_cards = [
                {
                    "name": p.name,
                    "icon": p.role.icon
                    if (player.game.initial_players == 3)
                    else "⭐️"
                    if isinstance(p.role, r.Sheriff)
                    else "🤠",
                    "avatar": p.avatar,
                    "alt_text": "".join(["❤️"] * p.lives)
                    + "".join(["💀"] * (p.max_lives - p.lives)),
                    "is_character": True,
                    "is_player": True,
                }
                for p in player.game.get_dead_players(include_ghosts=False)
            ]
            self.can_be_used_now = False
            player.game.deck.scrap(self, True)
            return True
        return False


class Lemat(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Lemat", number, is_equipment=True, is_weapon=True, range=1
        )
        self.icon = "🔫"  # ogni carta può essere usata come bang, conta per il conteggio dei bang per turno

    def play_card(self, player, against, _with=None):
        if not self.can_be_used_now and player.game.check_event(ce.Lazo):
            return False
        if self.can_be_used_now:
            if not super().play_card(player, against, _with):
                return False
            self.can_be_used_now = False
            return True
        elif not player.has_played_bang and any(
            (
                player.get_sight() >= p["dist"]
                for p in player.game.get_visible_players(player)
            )
        ):
            player.set_choose_action("choose_play_as_bang", player.hand.copy())
            player.notify_self()
        return False


class SerpenteASonagli(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "SerpenteASonagli", number, is_equipment=True)
        self.need_target = True
        self.icon = "🐍️"  # Ogni turno pesca se il seme picche -1hp
        self.alt_text = "♠️ =💔"

    def play_card(self, player, against, _with=None):
        if (player.game.check_event(ce.IlGiudice)) or not self.can_be_used_now:
            return False
        if against is not None:
            self.can_be_used_now = False
            G.sio.emit(
                "chat_message",
                room=player.game.name,
                data=f"_play_card_against|{player.name}|{self.name}|{against}",
            )
            player.game.get_player_named(against).equipment.append(self)
            player.game.get_player_named(against).notify_self()
            return True
        return False


class Shotgun(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Shotgun", number, is_equipment=True, is_weapon=True, range=1
        )
        self.icon = "🔫"  # Ogni volta che colpisci un giocatore deve scartare una carta


class Taglia(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Taglia", number, is_equipment=True)
        self.need_target = True
        self.icon = "💰"  # chiunque colpisca il giocatore con la taglia pesca una carta dal mazzo, si toglie solo con panico, cat balou, dalton

    def play_card(self, player, against, _with=None):
        if (player.game.check_event(ce.IlGiudice)) or not self.can_be_used_now:
            return False
        if against is not None:
            self.can_be_used_now = False
            G.sio.emit(
                "chat_message",
                room=player.game.name,
                data=f"_play_card_against|{player.name}|{self.name}|{against}",
            )
            player.game.get_player_named(against).equipment.append(self)
            player.game.get_player_named(against).notify_self()
            return True
        return False


class UltimoGiro(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "UltimoGiro", number)
        self.icon = "🥂"
        # self.desc = 'Recupera 1 vita'
        # self.desc_eng = 'Regain 1 HP'
        self.alt_text = "🍺"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against)
        player.lives = min(player.lives + 1, player.max_lives)
        player.notify_self()
        return True


class Tomahawk(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Tomahawk", number, range=2)
        self.icon = "🪓️"
        self.alt_text = "2🔎 💥"
        # "Spara a un giocatore a distanza 2"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against is not None and player.game.can_card_reach(self, player, against):
            super().play_card(player, against=against)
            player.game.attack(player, against, card_name=self.name)
            return True
        return False


class Tornado(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Tornado", number)
        self.icon = "🌪️"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.discard_others(player, card_name=self.name)
        return True


class Sventagliata(
    Bang
):  # : conta come un normale BANG! del turno. Il BANG! secondario è obbligatorio ed è sparato anche se il primo viene annullato, se si può, tu sei escluso come target
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = "Sventagliata"
        self.icon = "🎏"
        self.alt_text = "💥💥"  # spara al target e anche, a uno a distanza 1 dal target
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against is not None:
            if player.has_played_bang:
                return False
            t = player.game.get_player_named(against)
            
            # Get the indices of players in the game for direction checking
            alive_players = player.game.get_alive_players()
            
            # If there are less than 4 players, we can't have a valid direction
            # because in a 3-player game, the third player can't be in the same direction
            if len(alive_players) < 4:
                player.available_cards = []
                super().play_card(player, against=against)
                return True
            
            player_index = alive_players.index(player)
            target_index = alive_players.index(t)
            
            # Calculate the direction from player to target
            player_to_target = (target_index - player_index) % len(alive_players)
            
            # Get all visible players at distance 1 from the target
            visible_players = player.game.get_visible_players(t)
            
            # Filter out the player using the card and the first target
            # and ensure the target is at distance 1
            available_players = []
            for p in visible_players:
                if p["name"] != player.name and p["name"] != t.name and p["dist"] == 1:
                    p_obj = player.game.get_player_named(p["name"])
                    p_index = alive_players.index(p_obj)
                    
                    # Calculate the direction from target to potential second target
                    target_to_p = (p_index - target_index) % len(alive_players)
                    
                    # Check if the potential target is in the same direction from the first target
                    # as the first target is from the player
                    if (player_to_target == 1 and target_to_p == 1) or \
                       (player_to_target == len(alive_players) - 1 and target_to_p == len(alive_players) - 1):
                        available_players.append(p)
            
            if available_players:
                player.available_cards = [
                    dict(p, **{"original_target": against})
                    for p in available_players
                ]
                player.pending_action = PendingAction.CHOOSE
                player.choose_text = "choose_sventagliata"
            else:
                # No valid targets in the same direction, play as regular Bang
                player.available_cards = []
                super().play_card(player, against=against)
            return True
        return False


class Salvo(Card):  # puoi anche prevenire un danno inferto da te, duello?
    def __init__(self, suit, number):
        super().__init__(suit, "Salvo", number)
        self.icon = "😇️"
        self.alt_text = "👤😅"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if against is not None:
            # TODO
            # super().play_card(player, against=against)
            # player.game.attack(player, against, card_name=self.name)
            return True
        return False


class Mira(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Mira", number)
        self.icon = "👌🏻"
        self.need_with_only = "Bang"
        self.alt_text = "💥🃏💔💔"
        self.need_target = True
        self.need_with = True

    def play_card(self, player, against, _with=None):
        if against is not None and _with is not None and _with.name == "Bang!":
            super().play_card(player, against=against, _with=_with)
            player.game.attack(player, against, card_name=self.name)
            return True
        return False


class Bandidos(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Bandidos", number)
        self.icon = "🤠️"
        self.alt_text = "👤🃏🃏/💔"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.discard_others(player, card_name=self.name)
        return True


class Fuga(
    Card
):  # comprende indiani gatling etc, ma solo se carte marroni, le carte verdi valgono, attenzione alla classi ereditate
    def __init__(self, suit, number):
        super().__init__(suit, "Fuga", number)
        self.icon = "🏃🏻"
        self.alt_text = "❌"

    def play_card(self, player, against, _with=None):
        return False


class Poker(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Poker", number)
        self.icon = "🃏"
        self.alt_text = "👤🃏 🃏🃏"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.discard_others(player, card_name=self.name)
        return True


class RitornoDiFiamma(Mancato):
    def __init__(self, suit, number):
        super().__init__(suit, number)
        self.name = "RitornoDiFiamma"
        self.icon = "🔥"
        self.alt_text = "😅 | 💥"

    def play_card(self, player, against, _with=None):
        return False

    def use_card(self, player):
        player.notify_self()


def get_starting_deck() -> List[Card]:
    cards = [
        Fantasma(Suit.SPADES, 9),
        Fantasma(Suit.SPADES, 10),
        Lemat(Suit.DIAMONDS, 4),
        SerpenteASonagli(Suit.HEARTS, 7),
        Shotgun(Suit.SPADES, "K"),
        Taglia(Suit.CLUBS, 9),
        UltimoGiro(Suit.DIAMONDS, 8),
        Tomahawk(Suit.DIAMONDS, "A"),
        Sventagliata(Suit.SPADES, 2),
        # Salvo(Suit.HEARTS, 5),
        Bandidos(
            Suit.DIAMONDS, "Q"
        ),  # gli altri  giocatori scelgono se scartare 2 carte o perdere 1 punto vita
        Fuga(
            Suit.HEARTS, 3
        ),  # evita l'effetto di carte marroni (tipo panico cat balou) di cui sei bersaglio
        Mira(Suit.CLUBS, 6),
        Poker(
            Suit.HEARTS, "J"
        ),  # tutti gli altri scartano 1 carta a scelta, se non ci sono assi allora pesca 2
        RitornoDiFiamma(Suit.CLUBS, "Q"),  # un mancato che fa bang
        Tornado(Suit.CLUBS, "A"),
    ]
    for c in cards:
        c.expansion_icon = "👻️"
    return cards

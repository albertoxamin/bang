from __future__ import annotations
from typing import List, Set, Dict, Tuple, Optional, TYPE_CHECKING
import bang.expansions.fistful_of_cards.card_events as ce
import bang.expansions.high_noon.card_events as ceh
from abc import ABC, abstractmethod
from enum import IntEnum
import bang.roles as r
from globals import G

if TYPE_CHECKING:
    from bang.players import Player
    from bang.game import Game


class Suit(IntEnum):
    DIAMONDS = 0  # ♦
    CLUBS = 1  # ♣
    HEARTS = 2  # ♥
    SPADES = 3  # ♠
    GOLD = 4  # 🤑


class Card(ABC):
    sym = {"A": 1, "J": 11, "Q": 12, "K": 13}

    def __init__(
        self,
        suit: Suit,
        name: str,
        number,
        is_equipment: bool = False,
        is_weapon: bool = False,
        vis_mod: int = 0,
        sight_mod: int = 0,
        range: int = 99,
        desc: str = "",
    ):
        super().__init__()
        self.name = name
        self.suit = suit
        if type(number) == int:
            self.number = number
        else:
            self.number = self.sym[number]
        self.is_equipment = is_equipment
        self.is_weapon = is_weapon
        self.vis_mod = vis_mod
        self.sight_mod = sight_mod
        self.range = range
        if self.range != 0 and self.range != 99:
            self.alt_text = f"{self.range} 🔍"
        self.desc = desc  # deprecated, has been replaced by the card's description in the localization files (see i18n folder)
        self.need_target = False  # Cards that need a target like Bang
        self.can_target_self = False  # for example Panico and CatBalou
        self.can_be_used_now = True  # to check wether the green card can be used now
        self.usable_next_turn = False  # it will be True for Green Cards
        self.need_with = (
            False  # it will be true for cards that require a card to be discarded with
        )
        self.need_with_only = ""  # names of the cards allowed to be discarded with
        self.must_be_used = False  # used by LeggeDelWest

    def __str__(self):
        if str(self.suit).isnumeric():
            char = ["♦️", "♣️", "♥️", "♠️", "🤑"][int(self.suit)]
        else:
            char = self.suit
        return f"{self.name} {char}{self.number}"
        return super().__str__()

    def num_suit(self):
        return f"{['♦️', '♣️', '♥️', '♠️', '🤑'][int(self.suit)]}{self.number}"

    def reset_card(self):
        if self.usable_next_turn:
            self.can_be_used_now = False
        else:
            self.can_be_used_now = True
        if self.must_be_used:
            self.must_be_used = False

    def play_card(
        self, player: Player, against: str = None, _with: int = None
    ):  # self --> carta
        if (
            (player.game.check_event(ce.IlGiudice))
            and self.usable_next_turn
            and not self.can_be_used_now
        ):
            return False
        if self.is_equipment:
            if (player.game.check_event(ce.IlGiudice)) or not self.can_be_used_now:
                return False
            if self.is_weapon:
                has_weapon = False
                for i, card in enumerate(player.equipment):
                    if card.is_weapon:
                        player.game.deck.scrap(card, player=player)
                        player.equipment[i] = self
                        has_weapon = True
                        break
                if not has_weapon:
                    player.equipment.append(self)
            elif self.name in [
                c.name for c in player.equipment if not isinstance(c, Dinamite)
            ]:
                return False
            else:
                player.equipment.append(self)
            self.must_be_used = False
            self.can_be_used_now = False
        if against:
            G.sio.emit(
                "card_against",
                room=player.game.name,
                data={"player": player.name, "target": against, "card": self.__dict__},
            )
            G.sio.emit(
                "chat_message",
                room=player.game.name,
                data=f"_play_card_against|{player.name}|{self.name}|{against}",
            )
        else:
            G.sio.emit(
                "chat_message",
                room=player.game.name,
                data=f"_play_card|{player.name}|{self.name}",
            )
        return True

    def use_card(self, player):
        pass

    def is_duplicate_card(self, player: Player):
        return any(c.name == self.name for c in player.equipment) or any(
            c.name == self.name for c in player.gold_rush_equipment
        )

    def check_suit(self, game: Game, accepted: List[Suit]):
        if game.check_event(ceh.Benedizione):
            return Suit.HEARTS in accepted
        elif game.check_event(ceh.Maledizione):
            return Suit.SPADES in accepted
        return self.suit in accepted


class Barile(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Barile", number, is_equipment=True)
        self.icon = "🛢"
        self.alt_text = "♥️=😅"
        # self.desc = "Quando sei bersagliato da un Bang puoi estrarre la prima carta dalla cima del mazzo, se la carta estratta è del seme Cuori allora vale come un Mancato"
        # self.desc_eng = "When someone plays a Bang against you. You can flip the first card from the deck, if the suit is Hearts then it counts as a Missed card"


class Dinamite(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Dinamite", number, is_equipment=True)
        self.icon = "🧨"
        self.alt_text = "2-9♠️ = 🤯"
        # self.desc = "Giocando la Dinamite, posizionala davanti a te, resterà innocua per un intero giro. All'inizio del prossimo turno prima di pescare e prima di una eventuale estrazione (es. Prigione), estrai una carta dalla cima del mazzo. Se esce una carta tra il 2  il 9 di picche (compresi) allora la dinamite esplode: perdi 3 vite e scarta la carta, altrimenti passa la dinamite al giocatore successivo, il quale estrarà a sua volta dopo che tu avrai passato il tuo turno"
        # self.desc_eng = "When playing Dynamite, place it in front of you, it will remain harmless for a whole round. At the beginning of the next turn before drawing and before any card flip (eg Prison), flip a card from the top of the deck. If a card is between 2 and 9 of spades (inclusive) then the dynamite explodes: you lose 3 lives and discard the card, otherwise pass the dynamite to the next player, who will draw in turn after you have ended your turn"


class Mirino(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Mirino", number, is_equipment=True, sight_mod=1)
        self.icon = "🔎"
        self.alt_text = "-1"
        # self.desc = "Tu vedi gli altri giocatori a distanza -1"
        # self.desc_eng = "You see the other players at distance -1"


class Mustang(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Mustang", number, is_equipment=True, vis_mod=1)
        self.icon = "🐎"
        self.alt_text = "+1"
        # self.desc = "Gli altri giocatori ti vedono a distanza +1"
        # self.desc_eng = "The other players see you at distance +1"


class Prigione(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Prigione", number, is_equipment=True)
        self.icon = "⛓"
        # self.desc = "Equipaggia questa carta a un altro giocatore, tranne lo Sceriffo. Il giocatore scelto all'inizio del suo turno, prima di pescare dovrà estrarre: se esce Cuori scarta questa carta e gioca normalmente il turno, altrimenti scarta questa carta e salta il turno"
        # self.desc_eng = "Equip this card to another player, except the Sheriff. The player chosen at the beginning of his turn, must flip a card before drawing: if it's Hearts, discard this card and play the turn normally, otherwise discard this card and skip the turn"
        self.need_target = True
        self.alt_text = "♥️= 🆓"

    def play_card(self, player, against, _with=None):
        if player.game.check_event(ce.IlGiudice):
            return False
        if against is not None and not isinstance(
            player.game.get_player_named(against).role, r.Sheriff
        ):
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


class Remington(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Remington", number, is_equipment=True, is_weapon=True, range=3
        )
        self.icon = "🔫"
        # self.desc = "Puoi sparare a un giocatore che sia distante 3 o meno"
        # self.desc_eng = "You can shoot another player at distance 3 or less"


class RevCarabine(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Rev Carabine", number, is_equipment=True, is_weapon=True, range=4
        )
        self.icon = "🔫"
        # self.desc = "Puoi sparare a un giocatore che sia distante 4 o meno"
        # self.desc_eng = "You can shoot another player at distance 4 or less"


class Schofield(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Schofield", number, is_equipment=True, is_weapon=True, range=2
        )
        self.icon = "🔫"
        # self.desc = "Puoi sparare a un giocatore che sia distante 2 o meno"
        # self.desc_eng = "You can shoot another player at distance 2 or less"


class Volcanic(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Volcanic", number, is_equipment=True, is_weapon=True, range=1
        )
        self.icon = "🔫"
        # self.desc = "Puoi sparare a un giocatore che sia distante 1 o meno, tuttavia puoi giocare quanti bang vuoi"
        # self.desc_eng = "You can shoot another player at distance 1 or less, however you no longer have the limit of 1 Bang"


class Winchester(Card):
    def __init__(self, suit, number):
        super().__init__(
            suit, "Winchester", number, is_equipment=True, is_weapon=True, range=5
        )
        self.icon = "🔫"
        # self.desc = "Puoi sparare a un giocatore che sia distante 5 o meno"
        # self.desc_eng = "You can shoot another player at distance 5 or less"


class Bang(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Bang!", number)
        self.icon = "💥"
        # self.desc = "Spara a un giocatore a distanza raggiungibile. Se non hai armi la distanza di default è 1"
        # self.desc_eng = "Shoot a player in sight. If you do not have weapons, your is sight is 1"
        self.need_target = True

    def play_card(self, player, against, _with=None):
        if (
            player.game.check_event(ceh.Sermone) and not self.number == 42
        ):  # 42 gold rush
            return False
        if (
            (player.has_played_bang and not self.number == 42)
            and (
                not any((isinstance(c, Volcanic) for c in player.equipment))
                or player.game.check_event(ce.Lazo)
            )
            and against is not None
        ):  # 42 gold rush:
            return False
        elif against is not None:
            import bang.characters as chars

            super().play_card(player, against=against)
            if not (self.number == 42 and self.suit == Suit.GOLD):  # 42 gold rush
                player.bang_used += 1
                player.has_played_bang = (
                    True
                    if not player.game.check_event(ceh.Sparatoria)
                    else player.bang_used > 1
                )
            if player.character.check(player.game, chars.WillyTheKid):
                player.has_played_bang = False
            player.game.attack(
                player,
                against,
                double=player.character.check(player.game, chars.SlabTheKiller),
                card_name=self.name,
            )
            return True
        return False


class Birra(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Birra", number)
        self.icon = "🍺"
        # self.desc = "Gioca questa carta per recuperare un punto vita. Non puoi andare oltre al limite massimo del tuo personaggio. Se stai per perdere l'ultimo punto vita puoi giocare questa carta anche nel turno dell'avversario. La birra non ha più effetto se ci sono solo due giocatori"
        # self.desc_eng = "Play this card to regain a life point. You cannot heal more than your character's maximum limit. If you are about to lose your last life point, you can also play this card on your opponent's turn. Beer no longer takes effect if there are only two players"

    def play_card(self, player, against=None, _with=None, skipChecks=False):
        if player.game.check_event(ceh.IlReverendo):
            return False
        if not skipChecks:
            import bang.expansions.gold_rush.characters as grch

            madamYto = [
                p
                for p in player.game.get_alive_players()
                if p.character.check(player.game, grch.MadamYto) and self.number != 42
            ]
            for p in madamYto:
                player.game.deck.draw(True, player=p)
                p.notify_self()
            if "gold_rush" in player.game.expansions and self.number != 42:
                from bang.players import PendingAction

                player.available_cards = [
                    {"name": "Pepita", "icon": "💵️", "alt_text": "1", "noDesc": True},
                    self,
                ]
                player.choose_text = "choose_birra_function"
                player.pending_action = PendingAction.CHOOSE
                player.notify_self()
                return True
        if (
            len(player.game.get_alive_players()) != 2 or self.number == 42
        ) and player.lives < player.max_lives:
            super().play_card(player, against=against)
            player.lives = min(player.lives + 1, player.max_lives)
            import bang.expansions.dodge_city.characters as chd

            if player.character.check(player.game, chd.TequilaJoe):
                player.lives = min(player.lives + 1, player.max_lives)
            return True
        elif (
            len(player.game.get_alive_players()) == 2
            or player.lives == player.max_lives
        ):
            G.sio.emit(
                "chat_message",
                room=player.game.name,
                data=f"_spilled_beer|{player.name}|{self.name}",
            )
            return True
        return False


class CatBalou(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Cat Balou", number)
        self.icon = "💃"
        # self.desc = "Fai scartare una carta a un qualsiasi giocatore, scegli a caso dalla mano, oppure fra quelle che ha in gioco"
        # self.desc_eng = "Choose and discard a card from any other player."
        self.need_target = True
        self.can_target_self = True

    def play_card(self, player, against, _with=None):
        if (
            against is not None
            and (
                len(player.game.get_player_named(against).hand)
                + len(player.game.get_player_named(against).equipment)
            )
            > 0
            and (player.name != against or len(player.equipment) > 0)
        ):
            super().play_card(player, against=against)
            player.game.steal_discard(player, against, self)
            return True
        return False


class Diligenza(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Diligenza", number)
        self.icon = "🚡"
        self.alt_text = "🎴🎴"
        # self.desc = "Pesca 2 carte dalla cima del mazzo"
        # self.desc_eng = "Draw 2 cards from the deck."

    def play_card(self, player, against, _with=None):
        G.sio.emit(
            "chat_message",
            room=player.game.name,
            data=f"_diligenza|{player.name}|{self.name}",
        )
        for i in range(2):
            player.game.deck.draw(True, player)
        player.game.deck.flip_wildwestshow()
        return True


class Duello(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Duello", number)
        self.need_target = True
        self.icon = "⚔️"
        # self.desc = "Gioca questa carta contro un qualsiasi giocatore. A turno, cominciando dal tuo avversario, potete scartare una carta Bang!, il primo giocatore che non lo fa perde 1 vita"
        # self.desc_eng = "Play this card against any player. In turn, starting with your opponent, you can discard a Bang! Card, the first player who does not do so loses 1 life."

    def play_card(self, player, against, _with=None):
        if against is not None:
            super().play_card(player, against=against)
            player.game.duel(player, against)
            return True
        return False


class Emporio(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Emporio", number)
        self.icon = "🏪"
        # self.desc = "Scopri dal mazzo tante carte quanto il numero di giocatori vivi, a turno, partendo da te, scegliete una carta e aggiungetela alla vostra mano"
        # self.desc_eng = "Put on the table N cards from the deck, where N is the number of alive players, in turn, starting with you, choose a card and add it to your hand"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.emporio()
        return True


class Gatling(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Gatling", number)
        self.icon = "🛰"
        # self.desc = "Spara a tutti gli altri giocatori"
        # self.desc_eng = "Shoot all the other players"
        self.alt_text = "👥💥"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.attack_others(player, card_name=self.name)
        return True


class Indiani(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Indiani!", number)
        self.icon = "🏹"
        # self.desc = "Tutti gli altri giocatori devono scartare un Bang! o perdere una vita"
        # self.desc_eng = "All the other players must discard a Bang! or lose 1 Health Point"

    def play_card(self, player, against, _with=None):
        super().play_card(player, against=against)
        player.game.indian_others(player)
        return True


class Mancato(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Mancato!", number)
        self.icon = "😅"
        # self.desc = "Usa questa carta per annullare un bang"
        # self.desc_eng = "Use this card to cancel the effect of a bang"

    def play_card(self, player, against, _with=None):
        import bang.characters as chars

        if against is not None and player.character.check(
            player.game, chars.CalamityJanet
        ):
            if player.has_played_bang and (
                not any((isinstance(c, Volcanic) for c in player.equipment))
                or player.game.check_event(ce.Lazo)
            ):
                return False
            if player.game.check_event(ceh.Sermone):
                return False
            G.sio.emit(
                "chat_message",
                room=player.game.name,
                data=f"_special_calamity|{player.name}|{self.name}|{against}",
            )
            player.bang_used += 1
            player.has_played_bang = (
                True
                if not player.game.check_event(ceh.Sparatoria)
                else player.bang_used > 1
            )
            player.game.attack(player, against, card_name=self.name)
            return True
        return False


class Panico(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Panico!", number, range=1)
        self.icon = "😱"
        self.need_target = True
        self.can_target_self = True
        # self.desc = "Pesca una carta da un giocatore a distanza 1, scegli a caso dalla mano, oppure fra quelle che ha in gioco"
        # self.desc_eng = "Steal a card from a player at distance 1"

    def play_card(self, player, against, _with=None):
        if (
            against is not None
            and (
                len(player.game.get_player_named(against).hand)
                + len(player.game.get_player_named(against).equipment)
            )
            > 0
            and (player.name != against or len(player.equipment) > 0)
        ):
            super().play_card(player, against=against)
            player.game.steal_discard(player, against, self)
            return True
        return False


class Saloon(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "Saloon", number)
        # self.desc = "Tutti i giocatori recuperano un punto vita compreso chi gioca la carta"
        # self.desc_eng = "Everyone heals 1 Health point"
        self.icon = "🍻"
        self.alt_text = "👥🍺"

    def play_card(self, player, against, _with=None):
        G.sio.emit(
            "chat_message",
            room=player.game.name,
            data=f"_saloon|{player.name}|{self.name}",
        )
        for p in player.game.get_alive_players():
            p.lives = min(p.lives + 1, p.max_lives)
            p.notify_self()
        return True


class WellsFargo(Card):
    def __init__(self, suit, number):
        super().__init__(suit, "WellsFargo", number)
        # self.desc = "Pesca 3 carte dalla cima del mazzo"
        # self.desc_eng = "Draw 3 cards from the deck"
        self.icon = "💸"
        self.alt_text = "🎴🎴🎴"

    def play_card(self, player, against, _with=None):
        G.sio.emit(
            "chat_message",
            room=player.game.name,
            data=f"_wellsfargo|{player.name}|{self.name}",
        )
        for _ in range(3):
            player.game.deck.draw(True, player)
        player.game.deck.flip_wildwestshow()
        return True


def get_starting_deck(expansions: List[str]) -> List[Card]:
    from bang.expansions import DodgeCity, TheValleyOfShadows

    base_cards = [
        Barile(Suit.SPADES, "Q"),
        Barile(Suit.SPADES, "K"),
        Dinamite(Suit.HEARTS, 2),
        Mirino(Suit.SPADES, "A"),
        Mustang(Suit.HEARTS, 8),
        Mustang(Suit.HEARTS, 9),
        Prigione(Suit.SPADES, "J"),
        Prigione(Suit.HEARTS, 4),
        Prigione(Suit.SPADES, 10),
        Remington(Suit.CLUBS, "K"),
        RevCarabine(Suit.CLUBS, "A"),
        Schofield(Suit.CLUBS, "J"),
        Schofield(Suit.CLUBS, "Q"),
        Schofield(Suit.SPADES, "K"),
        Volcanic(Suit.SPADES, 10),
        Volcanic(Suit.CLUBS, 10),
        Winchester(Suit.SPADES, 8),
        Bang(Suit.SPADES, "A"),
        Bang(Suit.DIAMONDS, 2),
        Bang(Suit.DIAMONDS, 3),
        Bang(Suit.DIAMONDS, 4),
        Bang(Suit.DIAMONDS, 5),
        Bang(Suit.DIAMONDS, 6),
        Bang(Suit.DIAMONDS, 7),
        Bang(Suit.DIAMONDS, 8),
        Bang(Suit.DIAMONDS, 9),
        Bang(Suit.DIAMONDS, 10),
        Bang(Suit.DIAMONDS, "J"),
        Bang(Suit.DIAMONDS, "Q"),
        Bang(Suit.DIAMONDS, "K"),
        Bang(Suit.DIAMONDS, "A"),
        Bang(Suit.CLUBS, 2),
        Bang(Suit.CLUBS, 3),
        Bang(Suit.CLUBS, 4),
        Bang(Suit.CLUBS, 5),
        Bang(Suit.CLUBS, 6),
        Bang(Suit.CLUBS, 7),
        Bang(Suit.CLUBS, 8),
        Bang(Suit.CLUBS, 9),
        Bang(Suit.HEARTS, "Q"),
        Bang(Suit.HEARTS, "K"),
        Bang(Suit.HEARTS, "A"),
        Birra(Suit.HEARTS, 6),
        Birra(Suit.HEARTS, 7),
        Birra(Suit.HEARTS, 8),
        Birra(Suit.HEARTS, 9),
        Birra(Suit.HEARTS, 10),
        Birra(Suit.HEARTS, "J"),
        CatBalou(Suit.HEARTS, "K"),
        CatBalou(Suit.DIAMONDS, 9),
        CatBalou(Suit.DIAMONDS, 10),
        CatBalou(Suit.DIAMONDS, "J"),
        Diligenza(Suit.SPADES, 9),
        Diligenza(Suit.SPADES, 9),
        Duello(Suit.DIAMONDS, "Q"),
        Duello(Suit.SPADES, "J"),
        Duello(Suit.CLUBS, 8),
        Emporio(Suit.CLUBS, 9),
        Emporio(Suit.SPADES, "Q"),
        Gatling(Suit.HEARTS, 10),
        Indiani(Suit.DIAMONDS, "K"),
        Indiani(Suit.DIAMONDS, "A"),
        Mancato(Suit.CLUBS, 10),
        Mancato(Suit.CLUBS, "J"),
        Mancato(Suit.CLUBS, "Q"),
        Mancato(Suit.CLUBS, "K"),
        Mancato(Suit.CLUBS, "A"),
        Mancato(Suit.SPADES, 2),
        Mancato(Suit.SPADES, 3),
        Mancato(Suit.SPADES, 4),
        Mancato(Suit.SPADES, 5),
        Mancato(Suit.SPADES, 6),
        Mancato(Suit.SPADES, 7),
        Mancato(Suit.SPADES, 8),
        Panico(Suit.HEARTS, "J"),
        Panico(Suit.HEARTS, "Q"),
        Panico(Suit.HEARTS, "A"),
        Panico(Suit.DIAMONDS, 8),
        Saloon(Suit.HEARTS, 5),
        WellsFargo(Suit.HEARTS, 3),
    ]
    if "dodge_city" in expansions:
        base_cards.extend(DodgeCity.get_cards())
    if "the_valley_of_shadows" in expansions:
        base_cards.extend(TheValleyOfShadows.get_cards())
    return base_cards

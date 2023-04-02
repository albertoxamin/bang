from __future__ import annotations
from abc import ABC
from bang.expansions import *
from typing import List, TYPE_CHECKING
from globals import G

if TYPE_CHECKING:
    from bang.players import Player
    from bang.game import Game


class Character(ABC):
    """Base class for all characters"""

    def __init__(
        self,
        name: str,
        max_lives: int,
        sight_mod: int = 0,
        visibility_mod: int = 0,
        pick_mod: int = 0,
        desc: str = "",
    ):
        super().__init__()
        self.name = name
        self.max_lives = max_lives
        self.sight_mod = sight_mod
        self.visibility_mod = visibility_mod
        self.is_character = True
        self.pick_mod = pick_mod
        self.desc = desc
        self.icon = "🤷‍♂️"
        self.number = "".join(["❤️"] * self.max_lives)

    def check(self, game: Game, character: Character):
        """Check character type and if Sbornia is active"""
        import bang.expansions.high_noon.card_events as ceh

        if game.check_event(ceh.Sbornia):
            return False
        return isinstance(self, character)

    def special(self, player: Player, data):
        """Base for special actions that can be performed by a character"""
        import bang.expansions.high_noon.card_events as ceh

        if player.game.check_event(ceh.Sbornia):
            return False
        G.sio.emit(
            "chat_message",
            room=player.game.name,
            data=f"_use_special|{player.name}|{self.name}",
        )
        return True


class BartCassidy(Character):
    """Ogni volta che viene ferito, pesca una carta

    Each time he is hurt, he draws a card"""

    def __init__(self):
        super().__init__("Bart Cassidy", max_lives=4)
        self.icon = "💔"


class BlackJack(Character):
    """All'inizio del suo turno, quando deve pescare, mostra a tutti la seconda carta, se è Cuori o Quadri pesca una terza carta senza farla vedere

    At the beginning of his turn, when he has to draw, he shows everyone the second card, if it is Hearts or Diamonds he draws a third card without showing it
    """

    def __init__(self):
        super().__init__("Black Jack", max_lives=4)
        self.icon = "🎰"


class CalamityJanet(Character):
    """Può usare i Mancato! come Bang! e viceversa

    She can use the Missed! as Bang! and the other way around"""

    def __init__(self):
        super().__init__("Calamity Janet", max_lives=4)
        self.icon = "🔀"


class ElGringo(Character):
    """Ogni volta che perde un punto vita pesca una carta dalla mano del giocatore responsabile ma solo se il giocatore in questione ha carte in mano (una carta per ogni punto vita)

    Each time he is hurt, he draws a card from the hand of the attacking player"""

    def __init__(self):
        super().__init__("El Gringo", max_lives=3)
        self.icon = "🤕"
        # ovviamente la dinamite non è considerata danno inferto da un giocatore


class JesseJones(Character):
    """All'inizio del suo turno, quando deve pescare, può prendere la prima carta a caso dalla mano di un giocatore e la seconda dal mazzo

    When he has to draw his cards, he may draw the first card from the hand of another player
    """

    def __init__(self):
        super().__init__("Jesse Jones", max_lives=4)
        self.icon = "😜"


class Jourdonnais(Character):
    """Gioca come se avesse un Barile sempre attivo, nel caso in cui metta in gioco un Barile 'Reale' può estrarre due volte

    He plays as he had a Barrel always active, if he equips another Barrel, he can flip 2 cards
    """

    def __init__(self):
        super().__init__("Jourdonnais", max_lives=4)
        self.icon = "🛢"


class KitCarlson(Character):
    """All'inizio del suo turno, quando deve pescare, pesca tre carte, ne sceglie due da tenere in mano e la rimanente la rimette in cima la mazzo

    When he has to draw, he peeks 3 cards and chooses 2, putting the other card on the top of the deck
    """

    def __init__(self):
        super().__init__("Kit Carlson", max_lives=4)
        self.icon = "🤔"


class LuckyDuke(Character):
    """Ogni volta che deve estrarre, prende due carte dal mazzo, sceglie una delle due carte per l'estrazione, infine le scarta entrambe

    Every time he has to flip a card, he can flip 2 times"""

    def __init__(self):
        super().__init__("Lucky Duke", max_lives=4, pick_mod=1)
        self.icon = "🍀"


class PaulRegret(Character):
    """Gioca come se avesse una Mustang sempre attiva, nel caso in cui metta in gioco una Mustang 'Reale' l'effetto si somma tranquillamente

    The other players see him at distance +1"""

    def __init__(self):
        super().__init__("Paul Regret", max_lives=3, visibility_mod=1)
        self.icon = "🏇"


class PedroRamirez(Character):
    """All'inizio del suo turno, quando deve pescare, può prendere la prima carta dalla cima degli scarti e la seconda dal mazzo

    When he has to draw, he may pick the first card from the discarded cards"""

    def __init__(self):
        super().__init__("Pedro Ramirez", max_lives=4)
        self.icon = "🚮"


class RoseDoolan(Character):
    """Gioca come se avesse un Mirino sempre attivo, nel caso in cui metta in gioco una Mirino 'Reale' l'effetto si somma tranquillamente

    She sees the other players at distance -1"""

    def __init__(self):
        super().__init__("Rose Doolan", max_lives=4, sight_mod=1)
        self.icon = "🕵️‍♀️"


class SidKetchum(Character):
    """Può scartare due carte per recuperare un punto vita anche più volte di seguito a patto di avere carte da scartare, può farlo anche nel turno dell'avversario se stesse per morire

    He can discard 2 cards to regain 1HP"""

    def __init__(self):
        super().__init__("Sid Ketchum", max_lives=4)
        self.icon = "🤤"


class SlabTheKiller(Character):
    """Per evitare i suoi Bang servono due Mancato, un eventuale barile vale solo come un Mancato

    To dodge his Bang! cards other players need 2 Missed!"""

    def __init__(self):
        super().__init__("Slab The Killer", max_lives=4)
        self.icon = "🔪"
        # vale per tutte le carte bang non solo per la carta che si chiama Bang!


class SuzyLafayette(Character):
    """Appena rimane senza carte in mano pesca immediatamente una carta dal mazzo

    Whenever she has an empty hand, she draws a card"""

    def __init__(self):
        super().__init__("Suzy Lafayette", max_lives=4)
        self.icon = "🔂"


class VultureSam(Character):
    """Quando un personaggio viene eliminato prendi tutte le carte di quel giocatore e aggiungile alla tua mano, sia le carte in mano che quelle in gioco

    When a player dies, he gets all the cards in the dead's hand and equipments"""

    def __init__(self):
        super().__init__("Vulture Sam", max_lives=4)
        self.icon = "🦉"


class WillyTheKid(Character):
    """Questo personaggio può giocare quanti bang vuole nel suo turno

    He doesn't have limits to the amounts of bang he can use"""

    def __init__(self):
        super().__init__("Willy The Kid", max_lives=4)
        self.icon = "🎉"


def all_characters(expansions: List[str]):
    from bang.expansions import DodgeCity, TheValleyOfShadows, WildWestShow, GoldRush

    base_chars = [
        BartCassidy(),
        BlackJack(),
        CalamityJanet(),
        ElGringo(),
        JesseJones(),
        Jourdonnais(),
        KitCarlson(),
        LuckyDuke(),
        PaulRegret(),
        PedroRamirez(),
        RoseDoolan(),
        SidKetchum(),
        SlabTheKiller(),
        SuzyLafayette(),
        VultureSam(),
        WillyTheKid(),
    ]
    if "dodge_city" in expansions:
        base_chars.extend(DodgeCity.get_characters())
    if "gold_rush" in expansions:
        base_chars.extend(GoldRush.get_characters())
    if "the_valley_of_shadows" in expansions:
        base_chars.extend(TheValleyOfShadows.get_characters())
    if "wild_west_show" in expansions:
        base_chars.extend(WildWestShow.get_characters())
    return base_chars

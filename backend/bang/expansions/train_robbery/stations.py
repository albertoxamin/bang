from typing import TYPE_CHECKING
import bang.cards as cs
import bang.players as pl

if TYPE_CHECKING:
    from bang.players import Player


class StationCard:
    def __init__(self, name: str):
        self.name = name
        self.expansion = "train_robbery"
        self.price: list[dict] = []
        self.attached_train = None

    def discard_and_buy_train(self, player: "Player", card_index: int):
        """Discard the card and buy the train"""
        card = player.available_cards.pop(card_index)
        for i, card in enumerate(player.hand):
            if card == self:
                player.hand.pop(i)
                break
        else:
            player.lives -= 1
        card = player.hand.pop(card_index)
        player.game.deck.scrap(card, True, player=player)
        player.equipment.append(self.attached_train)
        self.attached_train = None
        player.pending_action = pl.PendingAction.PLAY

    def check_price(self, player: "Player") -> bool:
        """Check if the card can be used to rob the train"""
        return len(player.hand) > 0


class BoomTown(StationCard):
    """Discard a Bang! to rob the train"""

    def __init__(self):
        super().__init__("Boom Town")
        self.price = [cs.Bang(0, 0).__dict__]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            not isinstance(c, cs.Bang) for c in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if isinstance(c, cs.Bang)],
            self.discard_and_buy_train,
        )
        return True


class Caticor(StationCard):
    """Discard a Cat Balou or Panico to rob the train"""

    def __init__(self):
        super().__init__("Caticor")
        self.price = [cs.CatBalou(0, 0).__dict__, cs.Panico(0, 0).__dict__]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            not (isinstance(card, cs.CatBalou) or isinstance(card, cs.Panico))
            for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [
                c
                for c in player.hand
                if isinstance(c, cs.CatBalou) or isinstance(c, cs.Panico)
            ],
            self.discard_and_buy_train,
        )
        return True


class CreepyCreek(StationCard):
    """Discard a card of spades to rob the train"""

    def __init__(self):
        super().__init__("Creepy Creek")
        self.price = [{"icon": "♠️"}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            card.suit != cs.Suit.SPADES for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if c.suit == cs.Suit.SPADES],
            self.discard_and_buy_train,
        )
        return True


class CrownsHole(StationCard):
    """Discard a beer to rob the train"""

    def __init__(self):
        super().__init__("Crown's Hole")
        self.price = [cs.Birra(0, 0).__dict__]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            not isinstance(card, cs.Birra) for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if isinstance(c, cs.Birra)],
            self.discard_and_buy_train,
        )
        return True


class Deadwood(StationCard):
    """Discard an equipment card to rob the train"""

    def __init__(self):
        super().__init__("Deadwood")
        self.price = [{"is_equipment": True}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            not card.is_equipment for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if c.is_equipment],
            self.discard_and_buy_train,
        )
        return True


class Dodgeville(StationCard):
    """Discard a Missed! to rob the train"""

    def __init__(self):
        super().__init__("Dodgeville")
        self.price = [cs.Mancato(0, 0).__dict__]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            not isinstance(card, cs.Mancato) for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if isinstance(c, cs.Mancato)],
            self.discard_and_buy_train,
        )
        return True


class FortWorth(StationCard):
    """Discard a card with number 10, J, Q, K, A to rob the train"""

    def __init__(self):
        super().__init__("Fort Worth")
        self.price = [{"icon": "10\nJ\nQ\nK\nA"}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            card.number not in {1, 10, 11, 12, 13} for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if c.number in {1, 10, 11, 12, 13}],
            self.discard_and_buy_train,
        )
        return True


class Frisco(StationCard):
    """Discard a card of clubs to rob the train"""

    def __init__(self):
        super().__init__("Frisco")
        self.price = [{"icon": "♣️"}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            card.suit != cs.Suit.CLUBS for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if c.suit == cs.Suit.CLUBS],
            self.discard_and_buy_train,
        )
        return True


class MinersOath(StationCard):
    """Discard a card of diamonds to rob the train"""

    def __init__(self):
        super().__init__("Miner's Oath")
        self.price = [{"icon": "♦️"}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            card.suit != cs.Suit.DIAMONDS for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if c.suit == cs.Suit.DIAMONDS],
            self.discard_and_buy_train,
        )
        return True


class SanTafe(StationCard):
    """Discard a card of hearts to rob the train"""

    def __init__(self):
        super().__init__("San Tafe")
        self.price = [{"icon": "♥️"}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            card.suit != cs.Suit.HEARTS for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if c.suit == cs.Suit.HEARTS],
            self.discard_and_buy_train,
        )
        return True


class Tombrock(StationCard):
    """Lose 1 life point to rob the train"""

    def __init__(self):
        super().__init__("Tombrock")
        self.price = [{"icon": "💔"}]

    def check_price(self, player: "Player"):
        if player.lives <= 1:
            return False
        player.set_choose_action(
            "choose_buy_train",
            [{"icon": "💔"}],
            self.discard_and_buy_train,
        )
        return True


class Yooma(StationCard):
    """Discard a card with number between 2 and 9 to rob the train"""

    def __init__(self):
        super().__init__("Yooma")
        self.price = [{"icon": "2-9"}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and all(
            not (2 <= card.number <= 9) for card in player.hand
        ):
            return False
        player.set_choose_action(
            "choose_buy_train",
            [c for c in player.hand if 2 <= c.number <= 9],
            self.discard_and_buy_train,
        )
        return True


class VirginiaTown(StationCard):
    """Discard two cards to rob the train"""

    def __init__(self):
        super().__init__("Virginia Town")
        self.price = [{}, {}]

    def check_price(self, player: "Player"):
        if super().check_price(player) and len(player.hand) < 2:
            return False
        player.set_choose_action(
            "choose_buy_train",
            player.hand.copy(),
            self.discard_and_buy_train,
        )
        return True


def get_all_stations():
    """Return a list of all the station cards"""
    return [
        BoomTown(),
        Caticor(),
        CreepyCreek(),
        CrownsHole(),
        Deadwood(),
        Dodgeville(),
        FortWorth(),
        Frisco(),
        MinersOath(),
        SanTafe(),
        Tombrock(),
        Yooma(),
        VirginiaTown(),
    ]

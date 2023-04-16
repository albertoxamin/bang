import bang.cards as cs


class StationCard:
    def __init__(self, name: str):
        self.name = name
        self.expansion = "train_robbery"
        self.price: list[dict] = []

    def card_check(self, card: cs.Card):
        """Check if the card can be used to rob the train"""


class BoomTown(StationCard):
    """Discard a Bang! to rob the train"""

    def __init__(self):
        super().__init__("Boom Town")
        self.price = [cs.Bang(0, 0).__dict__]

    def card_check(self, card: cs.Card):
        return isinstance(card, cs.Bang)


class Caticor(StationCard):
    """Discard a Cat Balou or Panico to rob the train"""

    def __init__(self):
        super().__init__("Caticor")
        self.price = [cs.CatBalou(0, 0).__dict__, cs.Panico(0, 0).__dict__]

    def card_check(self, card: cs.Card):
        return isinstance(card, cs.CatBalou) or isinstance(card, cs.Panico)


class CreepyCreek(StationCard):
    """Discard a card of spades to rob the train"""

    def __init__(self):
        super().__init__("Creepy Creek")
        self.price = [{"icon": "♠️"}]

    def card_check(self, card: cs.Card):
        return card.suit == cs.Suit.SPADES


class CrownsHole(StationCard):
    """Discard a beer to rob the train"""

    def __init__(self):
        super().__init__("Crown's Hole")
        self.price = [cs.Birra(0, 0).__dict__]

    def card_check(self, card: cs.Card):
        return isinstance(card, cs.Birra)


class Deadwood(StationCard):
    """Discard an equipment card to rob the train"""

    def __init__(self):
        super().__init__("Deadwood")
        self.price = [{"is_equipment": True}]

    def card_check(self, card: cs.Card):
        return card.is_equipment


class Dodgeville(StationCard):
    """Discard a Missed! to rob the train"""

    def __init__(self):
        super().__init__("Dodgeville")
        self.price = [cs.Mancato(0, 0).__dict__]

    def card_check(self, card: cs.Card):
        return isinstance(card, cs.Mancato)


class FortWorth(StationCard):
    """Discard a card with number 10, J, Q, K, A to rob the train"""

    def __init__(self):
        super().__init__("Fort Worth")
        self.price = [{"icon": "10\nJ\nQ\nK\nA"}]

    def card_check(self, card: cs.Card):
        return card.number in {1, 10, 11, 12, 13}


class Frisco(StationCard):
    """Discard a card of clubs to rob the train"""

    def __init__(self):
        super().__init__("Frisco")
        self.price = [{"icon": "♣️"}]

    def card_check(self, card: cs.Card):
        return card.suit == cs.Suit.CLUBS


class MinersOath(StationCard):
    """Discard a card of diamonds to rob the train"""

    def __init__(self):
        super().__init__("Miner's Oath")
        self.price = [{"icon": "♦️"}]

    def card_check(self, card: cs.Card):
        return card.suit == cs.Suit.DIAMONDS


class SanTafe(StationCard):
    """Discard a card of hearts to rob the train"""

    def __init__(self):
        super().__init__("San Tafe")
        self.price = [{"icon": "♥️"}]

    def card_check(self, card: cs.Card):
        return card.suit == cs.Suit.HEARTS


class Tombrock(StationCard):
    """Lose 1 life point to rob the train"""

    def __init__(self):
        super().__init__("Tombrock")
        self.price = [{"icon": "💔"}]

    def card_check(self, card: cs.Card):
        return True


class Yooma(StationCard):
    """Discard a card with number between 2 and 9 to rob the train"""

    def __init__(self):
        super().__init__("Yooma")
        self.price = [{"icon": "2-9"}]

    def card_check(self, card: cs.Card):
        return 2 <= card.number <= 9


class VirginiaTown(StationCard):
    """Discard two cards to rob the train"""

    def __init__(self):
        super().__init__("Virginia Town")
        self.price = [{}, {}]

    def card_check(self, card: cs.Card):
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

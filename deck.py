import cards
import random

class Deck:
    def __init__(self):
        super().__init__()
        self.cards = cards.get_starting_deck()
        self.scrap_pile = []

    def peek(self, n_cards: int) -> list:
        return self.cards[:n_cards]

    def peek_scrap_pile(self,) -> cards.Card:
        if len(self.scrap_pile) > 0:
            return self.scrap_pile[-1]
        else:
            return None

    def pick_and_scrap(self) -> cards.Card:
        card = self.cards.pop(0)
        self.scrap_pile.append(card)
        return card

    def draw(self) -> cards.Card:
        card = self.cards.pop(0)
        if len(self.cards) == 0:
            self.cards = self.scrap_pile[:-1].copy()
            random.shuffle(self.cards)
            self.scrap_pile = self.scrap_pile[-1:]
        return card

    def draw_from_scrap_pile(self) -> cards.Card:
        if len(self.scrap_pile) > 0:
            return self.scrap_pile.pop(0)
        else:
            return self.draw()

    def scrap(self, card: cards.Card):
        self.scrap_pile.append(card)
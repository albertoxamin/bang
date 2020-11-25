from typing import List, Set, Dict, Tuple, Optional
import random
import cards as cs

class Deck:
    def __init__(self, game):
        super().__init__()
        self.cards: List[cs.Card] = cs.get_starting_deck()
        self.game = game
        random.shuffle(self.cards)
        self.scrap_pile: List[cs.Card] = []
        print(f'Deck initialized with {len(self.cards)} cards')

    def peek(self, n_cards: int) -> list:
        return self.cards[:n_cards]

    def peek_scrap_pile(self) -> cs.Card:
        if len(self.scrap_pile) > 0:
            return self.scrap_pile[-1]
        else:
            return None

    def pick_and_scrap(self) -> cs.Card:
        card = self.cards.pop(0)
        self.scrap_pile.append(card)
        self.game.notify_scrap_pile()
        return card

    def put_on_top(self, card: cs.Card):
        self.cards.insert(0, card)

    def draw(self) -> cs.Card:
        card = self.cards.pop(0)
        if len(self.cards) == 0:
            self.cards = self.scrap_pile[:-1].copy()
            random.shuffle(self.cards)
            self.scrap_pile = self.scrap_pile[-1:]
        return card

    def draw_from_scrap_pile(self) -> cs.Card:
        if len(self.scrap_pile) > 0:
            card = self.scrap_pile.pop(-1)
            self.game.notify_scrap_pile()
            return card
        else:
            return self.draw()

    def scrap(self, card: cs.Card):
        self.scrap_pile.append(card)
        self.game.notify_scrap_pile()

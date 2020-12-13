from typing import List, Set, Dict, Tuple, Optional
import random
import bang.cards as cs

class Deck:
    def __init__(self, game):
        super().__init__()
        self.cards: List[cs.Card] = cs.get_starting_deck(game.expansions)
        self.mancato_cards: List[str] = []
        self.mancato_cards_not_green: List[str] = []
        for c in self.cards:
            if isinstance(c, cs.Mancato) and c.name not in self.mancato_cards:
                self.mancato_cards.append(c.name)
                if not c.usable_next_turn:
                    self.mancato_cards_not_green.append(c.name)
        self.all_cards_str: List[str] = []
        for c in self.cards:
            if c.name not in self.all_cards_str:
                self.all_cards_str.append(c.name)
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
        if card.usable_next_turn:
            card.can_be_used_now = False
        self.scrap_pile.append(card)
        self.game.notify_scrap_pile()

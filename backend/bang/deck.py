from typing import List, Set, Dict, Tuple, Optional
import random
import bang.cards as cs
import bang.expansions.fistful_of_cards.card_events as ce
import bang.expansions.high_noon.card_events as ceh
import bang.expansions.gold_rush.shop_cards as grc
from globals import G

class Deck:
    def __init__(self, game):
        super().__init__()
        self.cards: List[cs.Card] = cs.get_starting_deck(game.expansions)
        self.mancato_cards: List[str] = []
        self.mancato_cards_not_green_or_blue: List[str] = []
        for c in self.cards:
            if isinstance(c, cs.Mancato) and c.name not in self.mancato_cards:
                self.mancato_cards.append(c.name)
                if not (c.usable_next_turn or c.is_equipment):
                    self.mancato_cards_not_green_or_blue.append(c.name)
        self.all_cards_str: List[str] = []
        for c in self.cards:
            if c.name not in self.all_cards_str:
                self.all_cards_str.append(c.name)
        self.game = game
        self.event_cards: List[ce.CardEvent] = []
        endgame_cards: List[ce.CardEvent] = []
        if 'fistful_of_cards' in game.expansions:
            self.event_cards.extend(ce.get_all_events(game.rng))
            endgame_cards.append(ce.get_endgame_card())
        if 'high_noon' in game.expansions:
            self.event_cards.extend(ceh.get_all_events(game.rng))
            endgame_cards.append(ceh.get_endgame_card())
        if len(self.event_cards) > 0:
            game.rng.shuffle(self.event_cards)
            self.event_cards = self.event_cards[:12]
            self.event_cards.insert(0, None)
            self.event_cards.insert(0, None) # 2 perchè iniziale, e primo flip dallo sceriffo
            self.event_cards.append(game.rng.choice(endgame_cards))
        game.rng.shuffle(self.cards)
        self.shop_deck: List[grc.ShopCard] = []
        self.shop_cards: List[grc.ShopCard] = []
        if 'gold_rush' in game.expansions:
            self.shop_cards = [None, None, None]
            self.shop_deck = grc.get_cards()
            game.rng.shuffle(self.shop_deck)
            self.fill_gold_rush_shop()
        self.scrap_pile: List[cs.Card] = []
        print(f'Deck initialized with {len(self.cards)} cards')

    def flip_event(self):
        if len(self.event_cards) > 0 and not (isinstance(self.event_cards[0], ce.PerUnPugnoDiCarte) or isinstance(self.event_cards[0], ceh.MezzogiornoDiFuoco)):
            self.event_cards.append(self.event_cards.pop(0))
        self.game.notify_event_card()

    def fill_gold_rush_shop(self):
        if not any((c is None for c in self.shop_cards)):
            return
        for i in range(3):
            if self.shop_cards[i] is None:
                print(f'replacing gr-card {i}')
                self.shop_cards[i] = self.shop_deck.pop(0)
                self.shop_cards[i].reset_card()
        self.game.notify_gold_rush_shop()

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
        if len(self.cards) == 0:
            self.reshuffle()
        self.game.notify_scrap_pile()
        return card

    def put_on_top(self, card: cs.Card):
        self.cards.insert(0, card)

    def draw(self, ignore_event = False, player=None) -> cs.Card:
        if self.game.check_event(ce.MinieraAbbandonata) and len(self.scrap_pile) > 0 and not ignore_event:
            return self.draw_from_scrap_pile()
        card = self.cards.pop(0)
        if len(self.cards) == 0:
            self.reshuffle()
        if player is not None and self.game.replay_speed > 0:
            G.sio.emit('card_drawn', room=self.game.name, data={'player': player.name, 'pile': 'deck'})
            player.hand.append(card)
        return card

    def reshuffle(self):
        self.cards = self.scrap_pile[:-1].copy()
        self.game.rng.shuffle(self.cards)
        self.scrap_pile = self.scrap_pile[-1:]

    def draw_from_scrap_pile(self) -> cs.Card:
        if len(self.scrap_pile) > 0:
            card = self.scrap_pile.pop(-1)
            self.game.notify_scrap_pile()
            card.reset_card()
            return card
        else:
            return self.draw()

    def scrap(self, card: cs.Card, ignore_event = False, player=None):
        if card.number == 42: return
        card.reset_card()
        if self.game.check_event(ce.MinieraAbbandonata) and not ignore_event:
            self.put_on_top(card)
        else:
            self.scrap_pile.append(card)
            if player is not None and self.game.replay_speed > 0:
                G.sio.emit('card_scrapped', room=self.game.name, data={'player': player.name, 'card':card.__dict__, 'pile': 'scrap'})
                G.sio.sleep(0.6)
                self.game.notify_scrap_pile()
            else:
                self.game.notify_scrap_pile()

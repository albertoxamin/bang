from typing import List, Set, Dict, Tuple, Optional, TYPE_CHECKING
import bang.cards as cs
import bang.expansions.fistful_of_cards.card_events as ce
import bang.expansions.high_noon.card_events as ceh
import bang.expansions.wild_west_show.card_events as cew
import bang.expansions.wild_west_show.characters as chw
import bang.expansions.gold_rush.shop_cards as grc
import bang.expansions.train_robbery.stations as trs
import bang.expansions.train_robbery.trains as trt
from globals import G

if TYPE_CHECKING:
    from bang.game import Game
    from bang.players import Player


class Deck:
    """Class that handles all deck dealing information"""

    def __init__(self, game: "Game"):
        super().__init__()
        self.cards: List[cs.Card] = cs.get_starting_deck(game.expansions)
        self.mancato_cards: List[str] = []
        self.mancato_cards_not_green_or_blue: List[str] = []
        self.green_cards: Set[str] = set()
        for c in self.cards:
            if isinstance(c, cs.Mancato) and c.name not in self.mancato_cards:
                self.mancato_cards.append(c.name)
                if not (c.usable_next_turn or c.is_equipment):
                    self.mancato_cards_not_green_or_blue.append(c.name)
            elif c.usable_next_turn:
                self.green_cards.add(c.name)
        self.all_cards_str: List[str] = []
        for c in self.cards:
            if c.name not in self.all_cards_str:
                self.all_cards_str.append(c.name)
        self.game = game
        self.event_cards: List[ce.CardEvent] = []
        self.event_cards_wildwestshow: List[ce.CardEvent] = []
        self.stations: List[trs.StationCard] = []
        self.train_pile: List[trt.TrainCard] = []
        self.current_train: List[trt.TrainCard] = []
        endgame_cards: List[ce.CardEvent] = []
        if "fistful_of_cards" in game.expansions:
            self.event_cards.extend(ce.get_all_events(game.rng))
            endgame_cards.append(ce.get_endgame_card())
        if "high_noon" in game.expansions:
            self.event_cards.extend(ceh.get_all_events(game.rng))
            endgame_cards.append(ceh.get_endgame_card())
        if "wild_west_show" in game.expansions:
            self.event_cards_wildwestshow.extend(cew.get_all_events(game.rng))
            game.rng.shuffle(self.event_cards_wildwestshow)
            self.event_cards_wildwestshow.insert(0, None)
            self.event_cards_wildwestshow.append(cew.get_endgame_card())
        if "train_robbery" in game.expansions:
            self.stations = game.rng.sample(trs.get_all_stations(), len(game.players))
            self.train_pile = trt.get_all_cards(game.rng)
            self.current_train = [trt.get_locomotives(game.rng)[0]] + self.train_pile[
                :3
            ]
        if len(self.event_cards) > 0:
            game.rng.shuffle(self.event_cards)
            self.event_cards = self.event_cards[:12]
            self.event_cards.insert(0, None)
            self.event_cards.insert(
                0, None
            )  # 2 perchè iniziale, e primo flip dallo sceriffo
            self.event_cards.append(game.rng.choice(endgame_cards))
        game.rng.shuffle(self.cards)
        self.shop_deck: List[grc.ShopCard] = []
        self.shop_cards: List[grc.ShopCard] = []
        if "gold_rush" in game.expansions:
            self.shop_cards = [None, None, None]
            self.shop_deck = grc.get_cards()
            game.rng.shuffle(self.shop_deck)
            self.fill_gold_rush_shop()
        self.scrap_pile: List[cs.Card] = []
        print(f"Deck initialized with {len(self.cards)} cards")

    def flip_event(self):
        """Flip event for regular Sheriff turn (High Noon, Fistful of Cards)"""
        if len(self.event_cards) > 0 and not (
            isinstance(self.event_cards[0], ce.PerUnPugnoDiCarte)
            or isinstance(self.event_cards[0], ceh.MezzogiornoDiFuoco)
        ):
            self.event_cards.append(self.event_cards.pop(0))
        if len(self.event_cards) > 0 and self.event_cards[0] is not None:
            self.event_cards[0].on_flipped(self.game)
        self.game.notify_event_card()
        self.game.notify_all()

    def flip_wildwestshow(self):
        """Flip event for Wild West Show only"""
        if len(self.event_cards_wildwestshow) > 0 and not isinstance(
            self.event_cards_wildwestshow[0], cew.WildWestShow
        ):
            self.event_cards_wildwestshow.append(self.event_cards_wildwestshow.pop(0))
        if (
            len(self.event_cards_wildwestshow) > 0
            and self.event_cards_wildwestshow[0] is not None
        ):
            self.event_cards_wildwestshow[0].on_flipped(self.game)
        self.game.notify_event_card_wildwestshow()
        self.game.notify_all()

    def fill_gold_rush_shop(self):
        """
        As gold_rush shop cards are stored in a fixed 3 space array,
        this function replaces the None values with new cards.
        """
        if not any((c is None for c in self.shop_cards)):
            return
        for i in range(3):
            if self.shop_cards[i] is None:
                print(f"replacing gr-card {i}")
                self.shop_cards[i] = self.shop_deck.pop(0)
                self.shop_cards[i].reset_card()
        self.game.notify_gold_rush_shop()

    def move_train_forward(self):
        if len(self.stations) == 0:
            return
        if len(self.current_train) == len(self.stations) + 4:
            return
        if len(self.current_train) > 0:
            self.current_train.append(None)
        self.game.notify_stations()

    def peek(self, n_cards: int) -> list:
        return self.cards[:n_cards]

    def peek_scrap_pile(self) -> cs.Card:
        if len(self.scrap_pile) > 0:
            return self.scrap_pile[-1]
        else:
            return None

    def pick_and_scrap(self) -> cs.Card:
        card = self.cards.pop(0)
        jpain = None
        for p in self.game.players:
            if p.character.check(self.game, chw.JohnPain) and len(p.hand) < 6:
                jpain = p
                break
        if jpain:
            jpain.hand.append(card)
            jpain.notify_self()
        else:
            self.scrap_pile.append(card)
        if len(self.cards) == 0:
            self.reshuffle()
        self.game.notify_scrap_pile()
        return card

    def put_on_top(self, card: cs.Card):
        self.cards.insert(0, card)

    def draw(self, ignore_event=False, player=None) -> cs.Card:
        if (
            self.game.check_event(ce.MinieraAbbandonata)
            and len(self.scrap_pile) > 0
            and not ignore_event
        ):
            card = self.draw_from_scrap_pile()
            if player is not None and self.game.replay_speed > 0:
                G.sio.emit(
                    "card_drawn",
                    room=self.game.name,
                    data={"player": player.name, "pile": "scrap"},
                )
                player.hand.append(card)
            return card
        card = self.cards.pop(0)
        if len(self.cards) == 0:
            self.reshuffle()
        if player is not None and self.game.replay_speed > 0:
            G.sio.emit(
                "card_drawn",
                room=self.game.name,
                data={"player": player.name, "pile": "deck"},
            )
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

    def scrap(self, card: cs.Card, ignore_event:bool=False, player:'Player'=None):
        if card.number == 42:
            return
        card.reset_card()
        if self.game.check_event(ce.MinieraAbbandonata) and not ignore_event:
            self.put_on_top(card)
        else:
            self.scrap_pile.append(card)
            if player is not None and self.game.replay_speed > 0:
                G.sio.emit(
                    "card_scrapped",
                    room=self.game.name,
                    data={
                        "player": player.name,
                        "card": card.__dict__,
                        "pile": "scrap",
                    },
                )
                G.sio.sleep(0.6)
                self.game.notify_scrap_pile()
            else:
                self.game.notify_scrap_pile()

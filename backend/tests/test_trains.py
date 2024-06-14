from random import randint
from bang.characters import Character
from bang.expansions.train_robbery.trains import *
from bang.deck import Deck
from bang.game import Game
from bang.players import Player
import bang.cards as cs
from globals import PendingAction

from tests import started_game, set_events, current_player, next_player, current_player_with_cards


def test_cattle_truck():
    g = started_game()

    g.deck.scrap_pile = [cs.CatBalou(0,1), cs.CatBalou(0,2), cs.CatBalou(0,3)]
    p = current_player_with_cards(g, [CattleTruck()])
    p.play_card(0)

    assert p.pending_action == PendingAction.CHOOSE
    p.choose(0)
    assert p.pending_action == PendingAction.PLAY
    assert len(p.hand) == 1
    assert len(g.deck.scrap_pile) == 2

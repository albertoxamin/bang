
from tests import started_game, set_events, current_player, next_player, current_player_with_cards

from bang.expansions.wild_west_show.card_events import *
from bang.cards import Card, Suit
import bang.roles as roles
from bang.players import PendingAction


# test Camposanto
def test_camposanto():
    g = started_game(['wild_west_show'], 4)
    set_events(g, [Camposanto()])
    current_player_with_cards(g, []).end_turn()
    p = current_player_with_cards(g, [])
    p.lives = 0
    p.notify_self()
    p1 = current_player_with_cards(g, [])
    p1.lives = 0
    p1.notify_self()
    current_player_with_cards(g, []).end_turn()
    current_player_with_cards(g, []).end_turn()
    assert p.is_my_turn
    assert p.lives == 1
    current_player_with_cards(g, []).end_turn()
    assert p1.is_my_turn
    assert p1.lives == 1


# test DarlingValentine
def test_darling_valentine():
    g = started_game(['wild_west_show'], 4)
    set_events(g, [DarlingValentine()])
    p = next_player(g)
    hand = p.hand.copy()
    current_player_with_cards(g, []).end_turn()
    assert hand != current_player(g).hand


# test DorothyRage

# test HelenaZontero
def test_helena_zontero():
    g = started_game(['wild_west_show'], 8)
    set_events(g, [None, HelenaZontero()])
    roles = [p.role.name for p in g.players]
    for i in range(len(g.players)-1):
        current_player_with_cards(g, []).end_turn()
    g.deck.cards = [Card(Suit.HEARTS, 'card', 0)]*5
    current_player_with_cards(g, []).end_turn()
    roles2 = [p.role.name for p in g.players]
    assert roles != roles2

# test LadyRosaDelTexas
def test_miss_suzanna():
    g = started_game(['wild_west_show'], 4)
    set_events(g, [None, LadyRosaDelTexas()])
    p = current_player_with_cards(g, [Card(0,'card',0)]*4)
    t = g.turn
    p.draw('event')
    assert g.turn == t+1

# test MissSusanna
def test_miss_suzanna():
    g = started_game(['wild_west_show'], 4)
    set_events(g, [MissSusanna()])
    p = current_player_with_cards(g, [])
    p.end_turn()
    assert p.lives == 4 # sceriffo 5-1
    p = current_player_with_cards(g, [Card(0,'card',0)]*4)
    p.play_card(0)
    p.play_card(0)
    p.play_card(0)
    p.end_turn()
    assert p.lives == 4
    p = current_player_with_cards(g, [])
    p.end_turn()
    assert p.lives == 3


# test RegolamentoDiConti
def test_miss_suzanna():
    g = started_game(['wild_west_show'], 4)
    set_events(g, [None, RegolamentoDiConti()])
    p = current_player_with_cards(g, [Card(0,'card',0)]*4)
    p.draw('event')
    assert p.pending_action == PendingAction.CHOOSE
    p.choose(0)


# test WildWestShow
def test_miss_suzanna():
    g = started_game(['wild_west_show'], 8)
    set_events(g, [None, WildWestShow()])
    for i in range(len(g.players)):
        current_player_with_cards(g, []).end_turn()
    for p in g.players:
        assert isinstance(p.role, roles.Renegade)

from tests import started_game, set_events, current_player, next_player, current_player_with_cards

from bang.expansions.wild_west_show.characters import *
from bang.cards import Card, Suit
import bang.roles as roles
from globals import PendingAction


# test TerenKill
def test_TerenKill():
    g = started_game(['wild_west_show'], 4, TerenKill())
    p = current_player_with_cards(g, [])
    p.lives = 0
    g.deck.cards = [Card(Suit.HEARTS, 'card', 0), Card(Suit.HEARTS, 'card', 0)]
    p.notify_self()
    assert p.lives == 1
    assert len(p.hand) == 1
    p.lives = 0
    g.deck.cards = [Card(Suit.SPADES, 'card', 0), Card(Suit.HEARTS, 'card', 0)]
    p.notify_self()
    assert p.lives == 0


# test YoulGrinner
def test_YoulGrinner():
    g = started_game(['wild_west_show'], 4, YoulGrinner())
    p = current_player(g)
    p.hand = []
    p.draw('')
    assert len(p.hand) == 5
    for pl in g.players:
        if pl != p:
            assert len(pl.hand) == 3

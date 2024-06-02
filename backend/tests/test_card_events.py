from tests import started_game, set_events, current_player, next_player, current_player_with_cards

from bang.expansions.fistful_of_cards.card_events import *
import bang.cards as cs


def test_miniera_abbandonata():
    g = started_game(['fistful_of_cards'])
    set_events(g, [MinieraAbbandonata()])
    p = current_player(g)
    starting_cards = len(p.hand)
    g.deck.scrap_pile = [
        cs.Bang(0, 0),
        cs.Bang(0, 1),
        cs.Bang(0, 2),
        cs.Bang(0, 3),
    ]
    p.draw("")
    assert len(p.hand) == starting_cards + 2
    # check the last two cards are the ones from the scrap pile
    assert p.hand[-2].name == cs.Bang(0, 0).name
    assert p.hand[-2].number == 3
    assert p.hand[-1].name == cs.Bang(0, 0).name
    assert p.hand[-1].number == 2

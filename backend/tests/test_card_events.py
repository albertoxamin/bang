from tests import started_game, set_events, current_player, next_player, current_player_with_cards
from bang.expansions.fistful_of_cards.card_events import *
from bang.expansions.high_noon.card_events import IDalton
from globals import PendingAction
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


def test_dalton():
    g = started_game(['high_noon'])
    # Create a player with blue cards
    p1 = current_player(g)
    p2 = next_player(g)
    
    # Give p1 a blue card (non-green equipment)
    blue_card = cs.Mustang(0, 1)  # Mustang is a blue card
    p1.equipment.append(blue_card)
    
    # Set up the Daltons event
    event = IDalton()
    set_events(g, [event])
    
    # Flip the event
    g.deck.flip_event()
    
    # Verify p1 is asked to discard (has blue card)
    assert p1.pending_action == PendingAction.CHOOSE
    assert p1.choose_text == "choose_dalton"
    assert len(p1.available_cards) == 1
    assert p1.available_cards[0] == blue_card
    
    # Verify p2 is not asked to discard (no blue cards)
    assert p2.pending_action != PendingAction.CHOOSE
    
    # Complete the event by having p1 discard their blue card
    p1.choose(0)  # Choose the first (and only) card to discard
    
    # Verify the card was discarded
    assert len(p1.equipment) == 0
    assert len(g.deck.scrap_pile) == 1
    assert g.deck.scrap_pile[0] == blue_card
    
    # Verify event completed
    assert g.dalton_on == False

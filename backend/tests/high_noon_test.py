from tests import started_game, set_events, current_player, next_player
from bang.expansions.high_noon.card_events import *
from globals import PendingAction
import bang.cards as cs


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


def test_reverend():
    g = started_game(['high_noon'])
    p1 = current_player(g)
    p2 = next_player(g)
    
    # Initial hands
    initial_p1_cards = len(p1.hand)
    initial_p2_cards = len(p2.hand)
    
    # Set up the Reverend event
    event = IlReverendo()
    set_events(g, [event])
    
    # Flip the event
    g.deck.flip_event()
    
    # Players can't play beer cards
    beer = cs.Birra(0, 1)
    p1.hand.append(beer)
    
    # Try to play beer
    initial_lives = p1.lives
    p1.play_card(len(p1.hand) - 1)
    
    # Verify beer was not effective
    assert p1.lives == initial_lives
    assert beer in p1.hand


def test_benedizione():
    g = started_game(['high_noon'])
    p1 = current_player(g)
    
    # Set up initial hand
    initial_cards = len(p1.hand)
    
    # Set up the Benedizione event
    event = Benedizione()
    set_events(g, [event])
    
    # Flip the event
    g.deck.flip_event()
    
    # Player should draw one extra card at the start of their turn
    p1.draw("")
    
    # Verify player got an extra card
    assert len(p1.hand) == initial_cards + 2  # Normal draw + blessing


def test_sermone():
    g = started_game(['high_noon'])
    p1 = current_player(g)
    
    # Give player some BANG! cards
    bang_card = cs.Bang(0, 1)
    p1.hand.append(bang_card)
    
    # Set up the Sermone event
    event = Sermone()
    set_events(g, [event])
    
    # Flip the event
    g.deck.flip_event()
    
    # Try to play BANG!
    initial_cards = len(p1.hand)
    p1.play_card(len(p1.hand) - 1)  # Try to play the BANG! card
    
    # Verify BANG! couldn't be played
    assert len(p1.hand) == initial_cards
    assert bang_card in p1.hand

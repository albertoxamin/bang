from bang.characters import Character
from backend.bang.cards import Bang, Barile, Suit, Volcanic
from tests.dummy_socket import DummySocket
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
from bang.cards import *

# test card Barile
def test_barile():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.set_character(p.available_characters[0].name)
    barrel_guy = g.players[g.turn]
    barrel_guy.character = Character('test_char', 2)
    barrel_guy.draw('')
    barrel_guy.hand = [Barile(0,0)]
    barrel_guy.play_card(0)
    assert isinstance(barrel_guy.equipment[0], Barile)
    barrel_guy.end_turn()
    barrel_guy.character = Character('test_char', 2)
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Volcanic(0,0), Bang(0,0), Bang(0,0)]
    g.players[g.turn].play_card(0)
    g.players[g.turn].play_card(0, barrel_guy.name)
    assert g.players[g.turn].pending_action == PendingAction.WAIT
    assert barrel_guy.pending_action == PendingAction.PICK
    g.deck.cards[0] = Bang(Suit.HEARTS, 5)
    barrel_guy.pick()
    assert barrel_guy.pending_action == PendingAction.WAIT
    assert barrel_guy.lives == barrel_guy.max_lives
    assert g.players[g.turn].pending_action == PendingAction.PLAY
    g.players[g.turn].play_card(0, barrel_guy.name)
    g.deck.cards[0] = Bang(Suit.SPADES, 5)
    barrel_guy.pick()
    assert barrel_guy.pending_action == PendingAction.WAIT
    assert barrel_guy.lives == barrel_guy.max_lives - 1
    assert g.players[g.turn].pending_action == PendingAction.PLAY

#test card Volcanic
def test_volcanic():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.set_character(p.available_characters[0].name)
        p.character = Character('test_char', 3)
        p.hand = []
    volcanic_guy = g.players[g.turn]
    volcanic_guy.draw('')
    volcanic_guy.hand = [Volcanic(0,0), Bang(0,0), Bang(0,0)]
    volcanic_guy.play_card(0)
    assert isinstance(volcanic_guy.equipment[0], Volcanic)
    volcanic_guy.play_card(0, g.players[(g.turn+1)%3].name)
    assert len(volcanic_guy.hand) == 1
    volcanic_guy.play_card(0, g.players[(g.turn+1)%3].name)
    assert len(volcanic_guy.hand) == 0

# test card Dinamite
def test_dinamite():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.set_character(p.available_characters[0].name)
        p.character = Character('test_char', 4)
        p.hand = []
    dinamite_guy = g.players[g.turn]
    dinamite_guy.draw('')
    dinamite_guy.hand = [Dinamite(0,0)]
    dinamite_guy.play_card(0)
    assert isinstance(dinamite_guy.equipment[0], Dinamite)
    dinamite_guy.end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    g.deck.cards.insert(0, Dinamite(Suit.HEARTS, 5))
    dinamite_guy.pick()
    assert len(dinamite_guy.equipment) == 0
    dinamite_guy.draw('')
    dinamite_guy.end_turn()
    assert len(g.players[g.turn].equipment) == 1
    g.deck.cards.insert(0, Dinamite(Suit.SPADES, 5))
    g.players[g.turn].pick()
    assert len(g.players[g.turn].equipment) == 0
    assert g.players[g.turn].lives == 1
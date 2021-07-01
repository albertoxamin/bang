from tests.dummy_socket import DummySocket
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
from bang.cards import *

def test_game_start():
    sio = DummySocket()
    g = Game('test', sio)
    p1 = Player('p1', 'p1', sio)
    g.add_player(p1)
    p2 = Player('p2', 'p2', sio)
    g.add_player(p2)
    p3 = Player('p3', 'p3', sio)
    g.add_player(p3)
    assert p1.role == None
    assert p2.role == None
    assert p3.role == None
    assert not g.started
    g.start_game()
    assert g.started
    assert p1.role != None
    assert p2.role != None
    assert p3.role != None
    assert len(p1.available_characters) == g.characters_to_distribute
    assert len(p2.available_characters) == g.characters_to_distribute
    assert len(p3.available_characters) == g.characters_to_distribute
    p1.set_character(p1.available_characters[0].name)
    assert p1.character != None
    p2.set_character(p2.available_characters[0].name)
    assert p2.character != None
    p3.set_character(p3.available_characters[0].name)
    assert p3.character != None
    assert g.players[g.turn].pending_action == PendingAction.DRAW

from random import randint
from bang.characters import *
from tests.dummy_socket import DummySocket
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
from bang.cards import *

def test_bartcassidy():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), BartCassidy()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if isinstance(g.players[g.turn].character, BartCassidy):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[(g.turn+1)%2].hand = []
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    assert len(g.players[(g.turn+1)%2].hand) == 0
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert len(g.players[(g.turn+1)%2].hand) == 1

def test_blackjack():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(1)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [BlackJack()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    g.players[g.turn].hand = []
    g.deck.cards.insert(1, Bang(Suit.HEARTS, 1))
    g.players[g.turn].draw('')
    assert len(g.players[g.turn].hand) == 3
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    g.deck.cards.insert(1, Bang(Suit.CLUBS, 1))
    g.players[g.turn].draw('')
    assert len(g.players[g.turn].hand) == 2
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    g.deck.cards.insert(1, Bang(Suit.DIAMONDS, 1))
    g.players[g.turn].draw('')
    assert len(g.players[g.turn].hand) == 3
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    g.deck.cards.insert(1, Bang(Suit.SPADES, 1))
    g.players[g.turn].draw('')
    assert len(g.players[g.turn].hand) == 2
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()

def test_calamityjanet():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), CalamityJanet()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if isinstance(g.players[g.turn].character, CalamityJanet):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[(g.turn+1)%2].hand = [Bang(0,0)]
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].pending_action == PendingAction.RESPOND
    g.players[(g.turn+1)%2].respond(0)
    g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Mancato(0,0)]
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].lives == 1

# TODO: Test ElGringo
# TODO: Test JesseJones
# TODO: Test Jourdonnais
# TODO: Test KitCarlson
# TODO: Test LuckyDuke
# TODO: Test PaulRegret
# TODO: Test PedroRamirez
# TODO: Test RoseDoolan
# TODO: Test SidKetchum
# TODO: Test SlabTheKiller
# TODO: Test SuzyLafayette

def test_VultureSam():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), Character('test_char', 4), VultureSam()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if isinstance(g.players[g.turn].character, VultureSam):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = [Bang(0,0), Bang(0,0), Bang(0,0), Bang(0,0)]
        g.players[g.turn].end_turn()
    while not isinstance(g.players[g.turn].character, VultureSam):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = [Bang(0,0), Bang(0,0), Bang(0,0), Bang(0,0)]
        g.players[g.turn].lives = 0
        g.players[g.turn].notify_self()
        assert len(g.players[2].hand) == 8
        return

def test_WillyTheKid():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), WillyTheKid()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if not isinstance(g.players[g.turn].character, WillyTheKid):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0), Bang(0,0), Bang(0,0)]
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].lives == 3
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].lives == 2
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].lives == 1
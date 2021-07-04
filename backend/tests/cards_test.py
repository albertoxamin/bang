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
        p.available_characters = [Character('test_char', 2)]
        p.set_character(p.available_characters[0].name)
    barrel_guy = g.players[g.turn]
    barrel_guy.draw('')
    barrel_guy.hand = [Barile(0,0)]
    barrel_guy.play_card(0)
    assert isinstance(barrel_guy.equipment[0], Barile)
    barrel_guy.end_turn()
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
        p.available_characters = [Character('test_char', 3)]
        p.set_character(p.available_characters[0].name)
    for p in ps:
        p.hand = []
    volcanic_guy = g.players[g.turn]
    volcanic_guy.draw('')
    volcanic_guy.hand = [Volcanic(0,0), Bang(0,0), Bang(0,0)]
    volcanic_guy.play_card(0)
    assert isinstance(volcanic_guy.equipment[0], Volcanic)
    assert volcanic_guy.get_sight() == 1
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
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    for p in ps:
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

# test mirino
def test_mirino():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(4)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    mirino_guy = g.players[g.turn]
    mirino_guy.draw('')
    mirino_guy.hand = [Mirino(0,0)]
    assert mirino_guy.get_sight(countWeapon=False) == 1
    mirino_guy.play_card(0)
    assert mirino_guy.get_sight(countWeapon=False) == 2

# test mustang
def test_mustang():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    mustang_guy = g.players[g.turn]
    mustang_guy.draw('')
    mustang_guy.hand = [Mustang(0,0)]
    assert mustang_guy.get_visibility() == 0
    mustang_guy.play_card(0)
    assert mustang_guy.get_visibility() == 1

# test Prigione
def test_prigione():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(4)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    sheriff = g.players[g.turn]
    sheriff.draw('')
    sheriff.hand = [Prigione(0,0)]
    sheriff.play_card(0, g.players[(g.turn+1)%4].name)
    assert len(sheriff.hand) == 0
    sheriff.end_turn()
    g.deck.cards.insert(0, Prigione(Suit.CLUBS, 5))
    skip_check = g.turn
    g.players[g.turn].pick()
    assert g.turn != skip_check
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Prigione(0,0)]
    g.players[g.turn].play_card(0, sheriff.name)
    assert len(g.players[g.turn].hand) == 1
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%4].name)
    g.players[g.turn].end_turn()
    g.deck.cards.insert(0, Prigione(Suit.HEARTS, 5))
    skip_check = g.turn
    g.players[g.turn].pick()
    assert g.turn == skip_check

# test all weapons ranges
def test_all_weapons():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(4)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Volcanic(0,0), Schofield(0,0), Remington(0,0), RevCarabine(0,0), Winchester(0,0)]
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].get_sight() == 1
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].get_sight() == 2
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].get_sight() == 3
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].get_sight() == 4
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].get_sight() == 5

# test bang
def test_bang():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0), Bang(0,0)]
    assert len(g.players[g.turn].hand) == 2
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert len(g.players[g.turn].hand) == 1
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert len(g.players[g.turn].hand) == 1

# test birra
def test_birra_2p():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Birra(0,0)]
    g.players[g.turn].lives = 1
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].lives == 1

# test birra
def test_birra_3p():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    initial_p = g.players[g.turn]
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Birra(0,0)]
    g.players[g.turn].lives = 1
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].lives == 2
    # test beer save
    g.players[g.turn].hand = [Birra(0,0)]
    g.players[g.turn].lives = 1
    g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, initial_p.name)
    assert initial_p.lives == 1
    # test non overflow
    g.players[g.turn].lives = g.players[g.turn].max_lives
    g.players[g.turn].hand = [Birra(0,0)]
    g.players[g.turn].play_card(0)
    assert g.players[g.turn].lives == g.players[g.turn].max_lives

# test CatBalou
#TODO

# test Diligenza
def test_diligenza():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(4)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Diligenza(0,0)]
    g.players[g.turn].play_card(0)
    assert len(g.players[g.turn].hand) == 2

# test Duello
#TODO

# test Emporio
#TODO

# test Gatling
#TODO

# test Indiani
#TODO

# test Mancato
#TODO

# test Panico
#TODO

# test Saloon
#TODO

# test WellsFargo
def test_diligenza():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(4)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [WellsFargo(0,0)]
    g.players[g.turn].play_card(0)
    assert len(g.players[g.turn].hand) == 3

from bang.characters import Character
from tests.dummy_socket import DummySocket
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
from bang.roles import *
from bang.cards import *

# test that a game with 3 player the deputy kills renegade and wins
def test_3p_deputy_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(3):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 3
    assert isinstance(g.players[g.turn].role, Vice)
    for i in range(3):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, against=g.players[roles['Rinnegato']].name)
    assert (hasattr(g.players[g.turn], 'win_status') and g.players[g.turn].win_status)
    assert not (hasattr(g.players[roles['Rinnegato']], 'win_status') and g.players[roles['Rinnegato']].win_status)
    assert not (hasattr(g.players[roles['Fuorilegge']], 'win_status') and g.players[roles['Fuorilegge']].win_status)

# test that a game with 3 player the renegade kills the outlaw and wins
def test_3p_renegade_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(3):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 3
    assert isinstance(g.players[g.turn].role, Vice)
    for i in range(3):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.turn = roles['Rinnegato']
    g.play_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, against=g.players[roles['Fuorilegge']].name)
    assert (hasattr(g.players[g.turn], 'win_status') and g.players[g.turn].win_status)
    assert not (hasattr(g.players[roles['Vice']], 'win_status') and g.players[roles['Vice']].win_status)
    assert not (hasattr(g.players[roles['Fuorilegge']], 'win_status') and g.players[roles['Fuorilegge']].win_status)

# test that a game with 3 player the outlaw kills the deputy and wins
def test_3p_outlaw_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(3):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 3
    assert isinstance(g.players[g.turn].role, Vice)
    for i in range(3):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.turn = roles['Fuorilegge']
    g.play_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, against=g.players[roles['Vice']].name)
    assert (hasattr(g.players[g.turn], 'win_status') and g.players[g.turn].win_status)
    assert not (hasattr(g.players[roles['Vice']], 'win_status') and g.players[roles['Vice']].win_status)
    assert not (hasattr(g.players[roles['Rinnegato']], 'win_status') and g.players[roles['Rinnegato']].win_status)

# test that a game with 4 player the outlaw kills the sheriff and win
def test_4p_outlaw_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(4):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 3
    assert isinstance(g.players[g.turn].role, Sheriff)
    for i in range(4):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.turn = roles['Fuorilegge']
    g.play_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, against=g.players[roles['Sceriffo']].name)
    for i in range(4):
        if isinstance(g.players[i].role, Outlaw):
            assert (hasattr(g.players[i], 'win_status') and g.players[i].win_status)
        else:
            assert not (hasattr(g.players[i], 'win_status') and g.players[i].win_status)

# test that a game with 5 player the renegade kills all the other players and wins
def test_5p_renegade_gatling_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(5):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 4
    assert isinstance(g.players[g.turn].role, Sheriff)
    g.players[g.turn].is_my_turn = False
    for i in range(len(g.players)):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.turn = roles['Rinnegato']
    g.play_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Gatling(0,0)]
    g.players[g.turn].play_card(0)
    for i in range(len(g.players)):
        if isinstance(g.players[i].role, Renegade):
            print (g.players[i].role.name, 'win_status:', hasattr(g.players[i], 'win_status') and g.players[i].win_status)
            assert (hasattr(g.players[i], 'win_status') and g.players[i].win_status)
        else:
            print(g.players[i].role.name, 'win_status:', (hasattr(g.players[i], 'win_status') and g.players[i].win_status))
            assert not (hasattr(g.players[i], 'win_status') and g.players[i].win_status)

# test that a game with 5 player the renegade kills all the other players and wins
def test_5p_renegade_indiani_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(5):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 4
    assert isinstance(g.players[g.turn].role, Sheriff)
    g.players[g.turn].is_my_turn = False
    for i in range(len(g.players)):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.turn = roles['Rinnegato']
    g.play_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Indiani(0,0)]
    g.players[g.turn].play_card(0)
    for i in range(len(g.players)):
        if isinstance(g.players[i].role, Renegade):
            print (g.players[i].role.name, 'win_status:', hasattr(g.players[i], 'win_status') and g.players[i].win_status)
            assert (hasattr(g.players[i], 'win_status') and g.players[i].win_status)
        else:
            print(g.players[i].role.name, 'win_status:', (hasattr(g.players[i], 'win_status') and g.players[i].win_status))
            assert not (hasattr(g.players[i], 'win_status') and g.players[i].win_status)

# test that a game with 5 player the renegade kills the sheriff but it isn't the last alive player and the outlaws wins
def test_5p_outlaw_death_win():
    sio = DummySocket()
    g = Game('test', sio)
    for i in range(5):
        p = Player(f'p{i}', f'p{i}', sio)
        g.add_player(p)
    g.start_game()
    for p in g.players:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    roles = {g.players[i].role.name:i for i in range(len(g.players))}
    print(roles)
    assert len(roles) == 4
    assert isinstance(g.players[g.turn].role, Sheriff)
    g.players[g.turn].is_my_turn = False
    for i in range(len(g.players)):
        g.players[i].lives = 1
        g.players[i].hand = []
    g.players[roles['Vice']].lives = 2
    g.turn = roles['Rinnegato']
    g.play_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Gatling(0,0)]
    g.players[g.turn].play_card(0)
    for i in range(len(g.players)):
        if isinstance(g.players[i].role, Outlaw):
            print (g.players[i].role.name, 'win_status:', hasattr(g.players[i], 'win_status') and g.players[i].win_status)
            assert (hasattr(g.players[i], 'win_status') and g.players[i].win_status)
            assert (hasattr(g.players[i], 'is_dead') and g.players[i].is_dead)
        else:
            print(g.players[i].role.name, 'win_status:', (hasattr(g.players[i], 'win_status') and g.players[i].win_status))
            assert not (hasattr(g.players[i], 'win_status') and g.players[i].win_status)

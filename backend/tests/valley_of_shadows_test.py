from random import randint
from bang.characters import Character
from bang.expansions.the_valley_of_shadows.cards import *
from tests.dummy_socket import DummySocket
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction

# test UltimoGiro
def test_ultimo_giro():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    ultimo_giro_guy = g.players[g.turn]
    ultimo_giro_guy.draw('')
    ultimo_giro_guy.lives = 3
    ultimo_giro_guy.hand = [UltimoGiro(0,0)]
    assert ultimo_giro_guy.lives == 3
    ultimo_giro_guy.play_card(0)
    assert ultimo_giro_guy.lives == 4

# test Tomahawk
def test_tomahawk():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(6)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    tomahawk_guy = g.players[g.turn]
    tomahawk_guy.draw('')
    tomahawk_guy.hand = [Tomahawk(0,0)]
    assert len(tomahawk_guy.hand) == 1
    tomahawk_guy.play_card(0, g.players[(g.turn+3)%6].name)
    assert len(tomahawk_guy.hand) == 1
    tomahawk_guy.play_card(0, g.players[(g.turn+1)%6].name)
    assert len(tomahawk_guy.hand) == 0

# test Fantasma
def test_fantasma():
    sio = DummySocket()
    g = Game('test', sio)
    ps = [Player(f'p{i}', f'p{i}', sio) for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    fantasma_guy = g.players[g.turn]
    fantasma_guy.lives = 0
    fantasma_guy.notify_self()
    pl = g.players[g.turn]
    pl.draw('')
    pl.hand = [Fantasma(0,0)]
    pl.play_card(0)
    assert pl.pending_action == PendingAction.CHOOSE
    assert pl.available_cards[0]['name'] == fantasma_guy.name
    pl.choose(0)
    assert pl.pending_action == PendingAction.PLAY
    assert len(fantasma_guy.equipment) == 1 and isinstance(fantasma_guy.equipment[0], Fantasma)

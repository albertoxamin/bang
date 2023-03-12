import pytest
from bang.characters import Character
from bang.game import Game
from bang.players import Player
from tests.dummy_socket import DummySocket
from globals import G
G.sio = DummySocket()


def started_game(expansions, players=4, character=Character('test_char', 4)):
    g = Game('test')
    g.expansions = expansions
    ps = [Player(f'p{i}', f'p{i}') for i in range(players)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [character]
        p.set_character(p.available_characters[0].name)
    return g


def set_events(g: Game, event_cards):
    g.deck.event_cards = event_cards


def current_player(g: Game):
    return g.players[g.turn]


def next_player(g: Game):
    return g.players[(g.turn + 1) % len(g.players)]


def current_player_with_cards(g: Game, cards):
    p = current_player(g)
    p.draw('')
    p.hand = cards
    return p

from bang.deck import Deck
from bang.game import Game
from bang.players import Player
from bang.roles import *
from bang.cards import *
from globals import PendingAction
from tests import started_game


# test that game can start
def test_game_start():
    g = Game("test")
    p1 = Player("p1", "p1")
    g.add_player(p1)
    p2 = Player("p2", "p2")
    g.add_player(p2)
    p3 = Player("p3", "p3")
    g.add_player(p3)
    assert p1.role is None
    assert p2.role is None
    assert p3.role is None
    assert not g.started
    g.start_game()
    assert g.started
    assert p1.role is not None
    assert p2.role is not None
    assert p3.role is not None
    assert len(p1.available_characters) == g.characters_to_distribute
    assert len(p2.available_characters) == g.characters_to_distribute
    assert len(p3.available_characters) == g.characters_to_distribute
    p1.set_character(p1.available_characters[0].name)
    assert p1.character is not None
    p2.set_character(p2.available_characters[0].name)
    assert p2.character is not None
    p3.set_character(p3.available_characters[0].name)
    assert p3.character is not None
    assert g.players[g.turn].pending_action == PendingAction.DRAW


# test that dodge_city is added to games with more than 8 players
def test_dodge_city():
    g = Game("test")
    for i in range(9):
        p = Player(f"p{i}", f"p{i}")
        g.add_player(p)
    assert "dodge_city" in g.expansions


# test that a game with 2 players has only renegade as role
def test_renegade_only():
    g = Game("test")
    p1 = Player("p1", "p1")
    g.add_player(p1)
    p2 = Player("p2", "p2")
    g.add_player(p2)
    g.start_game()
    assert isinstance(g.players[0].role, Renegade)
    assert isinstance(g.players[1].role, Renegade)


# test that a game with 3 player has Renegade, Vice and Outlaw as roles
def test_renegade_vice_outlaw():
    g = Game("test")
    for i in range(3):
        p = Player(f"p{i}", f"p{i}")
        g.add_player(p)
    g.start_game()
    roles = {p.role.name for p in g.players}
    assert len(roles) == 3


# test that a game with 4 players has all roles except the deputy
def test_4_players_roles():
    g = Game("test")
    for i in range(4):
        p = Player(f"p{i}", f"p{i}")
        g.add_player(p)
    g.start_game()
    roles = {p.role.name for p in g.players}
    assert len(roles) == 3


# test that a game with 5 players has all roles
def test_5_players_roles():
    g = Game("test")
    for i in range(5):
        p = Player(f"p{i}", f"p{i}")
        g.add_player(p)
    g.start_game()
    roles = {p.role.name for p in g.players}
    assert len(roles) == 4


def test_expansions():
    started_game(
        [
            "high_noon",
            "dodge_city",
            "gold_rush",
            "the_valley_of_shadows",
            "wild_west_show",
        ]
    )

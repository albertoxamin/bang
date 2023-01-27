from random import randint
from bang.characters import Character
from bang.expansions.dodge_city.cards import *
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
import bang.cards as cs

# test Borraccia
def test_Borraccia():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    borraccia_guy = g.players[g.turn]
    borraccia_guy.draw('')
    borraccia_guy.lives = 3
    borraccia_guy.hand = [Borraccia(0,0)]
    assert len(borraccia_guy.hand) == 1
    borraccia_guy.play_card(0)
    assert len(borraccia_guy.hand) == 0
    assert len(borraccia_guy.equipment) == 1
    assert not borraccia_guy.equipment[0].can_be_used_now
    borraccia_guy.play_card(0)
    assert len(borraccia_guy.hand) == 0
    assert len(borraccia_guy.equipment) == 1
    borraccia_guy.end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    borraccia_guy.draw('')
    assert borraccia_guy.equipment[0].can_be_used_now
    borraccia_guy.hand = []
    borraccia_guy.play_card(0)
    assert len(borraccia_guy.equipment) == 0
    assert borraccia_guy.lives == 4

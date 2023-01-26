from random import randint
from bang.characters import Character
from bang.expansions.the_valley_of_shadows.characters import *
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
import bang.cards as cs

# test TucoFranziskaner
def test_TucoFranziskaner():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [TucoFranziskaner()]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p.hand = []
    p.draw('')
    assert len(p.hand) == 4
    p.end_turn()
    p = g.players[g.turn]
    p.hand = []
    p.equipment = [cs.Barile(0,0)]
    p.draw('')
    assert len(p.hand) == 2

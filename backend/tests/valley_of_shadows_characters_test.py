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

# test ColoradoBill
def test_ColoradoBill():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [ColoradoBill()]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%2]
    p.draw('')
    p.hand = [cs.Volcanic(0,0), cs.Bang(0,0), cs.Bang(0,0)]
    p.play_card(0)
    g.deck.cards.insert(0, cs.Bang(cs.Suit.SPADES,0))
    g.deck.cards.insert(1, cs.Bang(cs.Suit.HEARTS,0))
    p1.hand = [cs.Mancato(0,0)]
    p.play_card(0, p1.name)
    assert len(p1.hand) == 1
    assert p1.lives == 3
    p.play_card(0, p1.name)
    assert p1.pending_action == PendingAction.RESPOND

# test BlackFlower
def test_BlackFlower():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [BlackFlower()]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p.draw('')
    p.hand = [cs.Volcanic(cs.Suit.DIAMONDS,0)]
    p.special('')
    assert p.pending_action == PendingAction.PLAY
    p.hand = [cs.Volcanic(cs.Suit.CLUBS,0)]
    p.special('')
    assert p.pending_action == PendingAction.CHOOSE

from tests.dummy_socket import DummySocket
from bang.deck import Deck
from bang.game import Game

def test_card_flip():
    g = Game('test')
    g.deck = Deck(g)
    l = len(g.deck.cards)
    assert g.deck.pick_and_scrap() is not None
    assert len(g.deck.cards) == l - 1
    assert len(g.deck.scrap_pile) == 1

def test_draw():
    g = Game('test')
    g.deck = Deck(g)
    l = len(g.deck.cards)
    assert g.deck.draw(True) is not None
    assert len(g.deck.cards) == l - 1
    assert len(g.deck.scrap_pile) == 0

def test_reshuffle():
    g = Game('test')
    g.deck = Deck(g)
    l = len(g.deck.cards)
    for i in range(80):
        assert g.deck.pick_and_scrap() is not None
    assert len(g.deck.cards) == 79
    assert len(g.deck.scrap_pile) == 1

def test_draw_from_scrap():
    g = Game('test')
    g.deck = Deck(g)
    l = len(g.deck.cards)
    assert g.deck.pick_and_scrap() is not None
    assert g.deck.draw_from_scrap_pile() is not None
    assert len(g.deck.cards) == 79
    assert len(g.deck.scrap_pile) == 0
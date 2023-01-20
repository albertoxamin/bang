from random import randint
from bang.characters import *
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
from bang.cards import *

def test_bartcassidy():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
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

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(1)]
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

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
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

def test_ElGringo():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), ElGringo()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if isinstance(g.players[g.turn].character, ElGringo):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[(g.turn+1)%2].hand = []
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0), Bang(0,0)]
    assert len(g.players[(g.turn+1)%2].hand) == 0
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert len(g.players[(g.turn+1)%2].hand) == 1
    assert len(g.players[g.turn].hand) == 0

def test_JesseJones():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), JesseJones()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if not isinstance(g.players[g.turn].character, JesseJones):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[(g.turn+1)%2].hand = [Bang(0,0)]
    g.players[g.turn].draw('p1' if g.turn == 0 else 'p0')
    g.players[g.turn].hand = [Bang(0,0), Bang(0,0)]
    assert len(g.players[(g.turn+1)%2].hand) == 0
    assert len(g.players[g.turn].hand) == 2

def test_Jourdonnais():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), Jourdonnais()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if isinstance(g.players[g.turn].character, Jourdonnais):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].pending_action == PendingAction.PICK

def test_KitCarlson():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), KitCarlson()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if not isinstance(g.players[g.turn].character, KitCarlson):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = [Mancato(0,0)]
        g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    assert g.players[g.turn].pending_action == PendingAction.CHOOSE
    assert len(g.players[g.turn].available_cards) == 3
    g.players[g.turn].choose(0)
    assert len(g.players[g.turn].available_cards) == 2
    g.players[g.turn].choose(1)
    assert g.players[g.turn].pending_action == PendingAction.PLAY

def test_LuckyDuke():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [LuckyDuke(), LuckyDuke()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    g.players[0].equipment = [Prigione(0,0)]
    g.players[1].equipment = [Prigione(0,0)]
    g.players[g.turn].draw('')
    g.players[g.turn].hand = []
    g.players[g.turn].end_turn()
    assert g.players[g.turn].pending_action == PendingAction.PICK
    g.deck.cards.insert(0, Bang(Suit.SPADES,0))
    g.deck.cards.insert(1, Bang(Suit.HEARTS,0))
    g.players[g.turn].pick()
    assert g.players[g.turn].pending_action == PendingAction.DRAW

def test_PaulRegret():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), PaulRegret()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    pls = g.get_visible_players(g.players[0])
    assert len(pls) == 1
    assert pls[0]['name'] == g.players[1].name
    assert pls[0]['dist'] > g.players[0].get_sight()

def test_PedroRamirez():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), PedroRamirez()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if not isinstance(g.players[g.turn].character, PedroRamirez):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.deck.scrap_pile.append(Bang(0,0))
    g.players[g.turn].hand = []
    g.players[g.turn].draw('scrap')
    assert len(g.players[g.turn].hand) == 2
    assert g.players[g.turn].hand[0].number == 0
    assert g.players[g.turn].hand[0].suit == 0
    assert isinstance(g.players[g.turn].hand[0], Bang)

def test_RoseDoolan():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 2), RoseDoolan()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    g.players[0].equipment = [Mustang(0,0)]
    g.players[0].notify_self()
    pls = g.get_visible_players(g.players[1])
    print(pls)
    assert len(pls) == 1
    assert pls[0]['name'] != g.players[1].name
    assert pls[0]['dist'] <= g.players[1].get_sight()

def test_SidKetchum():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), SidKetchum()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if not isinstance(g.players[g.turn].character, SidKetchum):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = []
        g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].lives = 1
    g.players[g.turn].scrap(0)
    assert g.players[g.turn].lives == 1
    g.players[g.turn].scrap(0)
    assert g.players[g.turn].lives == 2

def test_SlabTheKiller():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), SlabTheKiller()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    if not isinstance(g.players[g.turn].character, SlabTheKiller):
        g.players[g.turn].draw('')
        g.players[g.turn].hand = [Mancato(0,0)]
        g.players[g.turn].end_turn()
    g.players[g.turn].draw('')
    g.players[g.turn].hand = [Bang(0,0)]
    g.players[g.turn].play_card(0, g.players[(g.turn+1)%2].name)
    assert g.players[(g.turn+1)%2].pending_action == PendingAction.RESPOND
    g.players[(g.turn+1)%2].respond(0)
    assert g.players[(g.turn+1)%2].pending_action == PendingAction.WAIT
    assert g.players[(g.turn+1)%2].lives == 3

def test_SuzyLafayette():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    test_chars = [Character('test_char', 4), SuzyLafayette()]
    for p in ps:
        p.available_characters = [test_chars.pop(0)]
        p.set_character(p.available_characters[0].name)
    g.players[1].hand = []
    assert len(g.players[1].hand) == 0
    g.players[1].notify_self()
    assert len(g.players[1].hand) == 1
    g.players[g.turn].end_turn()

def test_VultureSam():

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
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

    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
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
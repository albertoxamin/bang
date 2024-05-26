from random import randint
from bang.characters import Character
from bang.expansions.the_valley_of_shadows.cards import *
from bang.deck import Deck
from bang.game import Game
from bang.players import Player, PendingAction
import bang.cards as cs

# test UltimoGiro
def test_ultimo_giro():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
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
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(6)]
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
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
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

# test SerpenteASonagli
def test_serpente_a_sonagli():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    serp = g.players[(g.turn+1)%3]
    p.draw('')
    p.hand = [SerpenteASonagli(0,0)]
    assert len(p.hand) == 1
    p.play_card(0, serp.name)
    assert len(p.hand) == 0
    assert len(serp.equipment) == 1 and isinstance(serp.equipment[0], SerpenteASonagli)
    p.end_turn()
    assert serp.pending_action == PendingAction.PICK
    g.deck.cards[0] = Bang(Suit.SPADES, 5)
    serp.pick()
    assert serp.lives == 3
    serp.draw('')
    serp.hand = [SerpenteASonagli(0,0)]
    serp.play_card(0, g.players[(g.turn+1)%3].name)
    assert len(serp.hand) == 0
    serp.end_turn()
    assert g.players[g.turn].pending_action == PendingAction.PICK
    g.deck.cards[0] = Bang(Suit.HEARTS, 5)
    g.players[g.turn].pick()
    assert g.players[g.turn].lives == 4

# test RitornoDiFiamma
def test_ritorno_di_fiamma():
    g = Game('test')
    g.expansions = ['the_valley_of_shadows']
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%3]
    p.draw('')
    p.hand = [Bang(1, 1)]
    p1.hand = [RitornoDiFiamma(0,0)]
    p.play_card(0, p1.name)
    assert len(p.hand) == 0
    assert len(p1.hand) == 1
    p1.respond(0)
    assert len(p1.hand) == 0
    assert p.lives == 3
    p.end_turn()
    assert p1.is_my_turn
    p1.draw('')
    p1.hand = [Bang(1, 1)]
    p.equipment = [cs.Barile(0,0)]
    p.hand = [RitornoDiFiamma(0,0)]
    p1.play_card(0, p.name)
    assert p.pending_action == PendingAction.PICK
    g.deck.cards[0] = Bang(Suit.SPADES, 5)
    p.pick()
    assert p.pending_action == PendingAction.RESPOND
    p.respond(0)
    assert p1.lives == 3

# test RitornoDiFiamma with gatling
def test_ritorno_di_fiamma_gatling():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
    g.expansions = ['the_valley_of_shadows']
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%3]
    p2 = g.players[(g.turn+2)%3]
    p.draw('')
    p.hand = [cs.Gatling(1, 1), Mancato(0,0)]
    p1.hand = [RitornoDiFiamma(0,0)]
    p2.hand = [Mancato(0,0)]
    p.play_card(0)
    assert len(p.hand) == 1
    assert p1.pending_action == PendingAction.RESPOND
    assert p2.pending_action == PendingAction.RESPOND
    p1.respond(0)
    assert p2.pending_action == PendingAction.RESPOND
    assert p.pending_action == PendingAction.WAIT
    p2.respond(0)
    # end of gatling
    assert p.pending_action == PendingAction.RESPOND
    p.respond(0)
    assert len(p.hand) == 0
    assert p.pending_action == PendingAction.PLAY

# test Taglia
def test_taglia():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%3]
    p.draw('')
    p.hand = [Taglia(0,0), Bang(1, 1)]
    p1.hand = []
    p.play_card(0, p1.name)
    assert len(p.hand) == 1
    assert len(p1.equipment) == 1
    assert len(p1.hand) == 0
    p.play_card(0, p1.name)
    assert p1.lives == 3
    assert len(p.hand) == 1

# test Bandidos
def test_bandidos():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%3]
    p.draw('')
    p.hand = [Bandidos(0,0), Bandidos(0,0)]
    p.play_card(0)
    assert len(p.hand) == 1
    assert p.pending_action == PendingAction.WAIT
    assert p1.pending_action == PendingAction.CHOOSE
    p1.choose(len(p1.hand))
    assert p1.lives == 3
    assert p.pending_action == PendingAction.PLAY
    p.play_card(0)
    assert len(p.hand) == 0
    assert p.pending_action == PendingAction.WAIT
    assert p1.pending_action == PendingAction.CHOOSE
    p1.choose(0)
    assert p1.pending_action == PendingAction.CHOOSE
    p1.choose(0)
    assert p1.pending_action == PendingAction.WAIT
    assert p.pending_action == PendingAction.PLAY

# test Poker
def test_poker():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%3]
    p.draw('')
    p.hand = [Poker(0,0), Poker(0,0)]
    p1.hand = [Bang(1, 1), Bang(2, 2)]
    p.play_card(0)
    assert len(p.hand) == 1
    assert p.pending_action == PendingAction.WAIT
    assert p1.pending_action == PendingAction.CHOOSE
    p1.choose(0)
    assert p.pending_action == PendingAction.PLAY
    p.play_card(0)
    assert p.pending_action == PendingAction.WAIT
    assert p1.pending_action == PendingAction.CHOOSE
    p1.choose(0)
    assert p.pending_action == PendingAction.CHOOSE
    p.choose(0)
    assert p1.pending_action == PendingAction.WAIT
    assert p.pending_action == PendingAction.PLAY
    assert len(p.hand) == 1

# test Tornado
def test_tornado():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(2)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)
    p = g.players[g.turn]
    p1 = g.players[(g.turn+1)%3]
    p.draw('')
    p.hand = [Tornado(0,0), Bang(1, 1)]
    p1.hand = [Bang(2, 2)]
    p.play_card(0)
    assert len(p.hand) == 1
    assert p.pending_action == PendingAction.CHOOSE
    assert p1.pending_action == PendingAction.CHOOSE
    p.choose(0)
    p1.choose(0)
    assert p.pending_action == PendingAction.PLAY
    assert len(p.hand) == 2
    assert len(p1.hand) == 2


def test_sventagliata():
    g = Game('test')
    ps = [Player(f'p{i}', f'p{i}') for i in range(3)]
    for p in ps:
        g.add_player(p)
    g.start_game()
    for p in ps:
        p.available_characters = [Character('test_char', 4)]
        p.set_character(p.available_characters[0].name)

    p = g.players[g.turn]
    p1 = g.players[(g.turn + 1) % 3]
    p2 = g.players[(g.turn + 2) % 3]
    
    p.draw('')
    p.hand = [Sventagliata('Hearts', 10), Bang('Hearts', 10)]
    p1.hand = [Mancato('Spades', 2)]
    p2.hand = [Mancato('Clubs', 5)]

    # Play Sventagliata
    p.play_card(0, against=p1.name)
    assert p.pending_action == PendingAction.CHOOSE
    assert len(p.available_cards) > 0  # Ensure there are available targets

    # Simulate choosing a secondary target
    secondary_target = p.available_cards[0]['name']
    assert secondary_target != p.name and secondary_target != p1.name  # Ensure the secondary target is correct
    p.choose(0)  # Choose the first available target

    assert p.pending_action == PendingAction.WAIT
    assert p1.pending_action == PendingAction.RESPOND

    # Simulate p1 responding to the Bang
    p1.respond(0)  # Assuming p1 plays a Mancato card in response
    assert p1.pending_action == PendingAction.WAIT
    assert p.pending_action == PendingAction.WAIT
    
    p2.respond(0)  # Assuming p2 plays a Mancato card in response
    assert p2.pending_action == PendingAction.WAIT
    assert p.pending_action == PendingAction.PLAY

    # check bang cannot be played
    assert len(p.hand) == 1
    p.play_card(0, against=p2.name)
    assert p.pending_action == PendingAction.PLAY
    assert len(p.hand) == 1
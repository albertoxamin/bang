from typing import List, Set, Dict, Tuple, Optional
import random
import socketio
import players
from characters import all_characters
from deck import Deck
from players import Player
import roles

class Game:
    def __init__(self, name, sio:socketio):
        super().__init__()
        self.sio = sio
        self.name = name
        self.players: List[players.Player] = []
        self.deck: Deck = None
        self.started = False
        self.turn = 0
        self.readyCount = 0

    def handle_disconnect(self, player: players.Player):
        print(f'player {player.name} left the game {self.name}')
        self.players.pop(self.players.index(player))
        if len(self.players) == 0:
            print(f'no players left in game {self.name}')
            return True
        self.sio.emit('room', room=self.name, data={'name': self.name, 'started': self.started, 'players': [p.name for p in self.players]})
        self.sio.emit('chat_message', room=self.name, data=f'{player.name} si è disconnesso.')
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        return False

    def add_player(self, player: players.Player):
        if player in self.players:
            return
        player.join_game(self)
        self.players.append(player)
        print(f'Added player {player.name} to game')
        self.sio.emit('room', room=self.name, data={'name': self.name, 'started': self.started, 'players': [p.name for p in self.players]})
        self.sio.emit('chat_message', room=self.name, data=f'{player.name} è entrato nella lobby.')

    def notify_character_selection(self):
        self.readyCount += 1
        if self.readyCount == len(self.players):
            self.distribute_roles()

    def choose_characters(self):
        char_cards = random.sample(all_characters(), len(self.players)*2)
        for i in range(len(self.players)):
            self.players[i].set_available_character(char_cards[i * 2 : i * 2 + 2])

    def start_game(self):
        print('GAME IS STARING')
        if self.started:
            return
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        self.sio.emit('chat_message', room=self.name, data=f'La partita sta iniziando...')
        self.sio.emit('start', room=self.name)
        self.started = True
        self.deck = Deck(self)
        self.choose_characters()

    def distribute_roles(self):
        available_roles: List[roles.Role] = []
        if len(self.players) == 3:
            available_roles = [roles.Sheriff(), roles.Renegade(), roles.Outlaw()]
        random.shuffle(available_roles)
        for i in range(len(self.players)):
            self.players[i].set_role(available_roles[i])
            if type(available_roles[i]) == roles.Sheriff:
                self.turn = i
            self.players[i].prepare()
            for k in range(self.players[i].max_lives):
                self.players[i].hand.append(self.deck.draw())
            self.players[i].notify_self()
        self.play_turn()

    def get_visible_players(self, player):
        i = self.players.index(player)
        sight = player.get_sight()
        return [{
            'name': self.players[j].name,
            'dist': min(abs(i - j), abs(i - len(self.players) - j)) + self.players[j].get_visibility(),
            'lives': self.players[j].lives,
            'max_lives': self.players[j].max_lives,
        } for j in range(len(self.players)) if i != j]

    def attack(self, attacker:Player, target_username:str):
        self.sio.emit('chat_message', room=self.name, data=f'{attacker.name} ha fatto Bang contro {target_username}.')
        if self.players[self.players_map[target_username]].get_banged():
            attacker.pending_action = players.PendingAction.WAIT
            attacker.notify_self()
    
    def responders_did_respond(self):
        self.players[self.turn].pending_action = players.PendingAction.PLAY
        self.players[self.turn].notify_self()

    def next_player(self):
        return self.players[(self.turn + 1) % len(self.players)]

    def play_turn(self):
        self.players[self.turn].play_turn()

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)
        self.play_turn()

    def notify_scrap_pile(self):
        print('scrap')
        self.sio.emit('scrap', room=self.name, data=self.deck.peek_scrap_pile().__dict__)

    def player_death(self, player: players.Player):
        print(f'player {player.name} died')
        self.players.pop(self.players.index(player))
        if len(self.players) == 0:
            print(f'no players left in game {self.name}')
            return True
        self.sio.emit('room', room=self.name, data={'name': self.name, 'started': self.started, 'players': [p.name for p in self.players]})
        self.sio.emit('chat_message', room=self.name, data=f'{player.name} è morto.')
        for p in self.players:
            p.notify_self()
        self.players_map = {c.name: i for i, c in enumerate(self.players)}


# game = Game()
# p1 = players.Player('p1')
# game.add_player(p1)
# p2 = players.Player('p2')
# game.add_player(p2)
# p3 = players.Player('p3')
# game.add_player(p3)
# game.start_game()
# for p in game.players:
#     p.set_character(random.choice(p.available_characters))
# game.distribute_roles()

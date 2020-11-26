
from typing import List, Set, Dict, Tuple, Optional
import random
import socketio
import bang.players as players
import bang.characters as characters
from bang.deck import Deck
import bang.roles as roles

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
        self.waiting_for = 0
        self.initial_players = 0
        self.password = ''
        self.expansions = []

    def notify_room(self):
        self.sio.emit('room', room=self.name, data={
            'name': self.name,
            'started': self.started,
            'players': [{'name':p.name, 'ready': False} for p in self.players],
            'password': self.password,
            'expansions': self.expansions,
        })

    def toggle_expansion(self, expansion_name):
        if not self.started:
            print('toggling', expansion_name)
            if expansion_name in self.expansions:
                self.expansions.remove(expansion_name)
            else:
                self.expansions.append(expansion_name)
            self.notify_room()

    def add_player(self, player: players.Player):
        if player in self.players or len(self.players) >= 7:
            return
        player.join_game(self)
        self.players.append(player)
        print(f'Added player {player.name} to game')
        self.notify_room()
        self.sio.emit('chat_message', room=self.name, data=f'{player.name} è entrato nella lobby.')

    def set_private(self):
        if self.password == '':
            self.password = ''.join(random.choice("AEIOUJKZT123456789") for x in range(6))
            print(self.name, 'is now private pwd', self.password)
        else:
            self.password = ''
        self.notify_room()

    def notify_character_selection(self):
        self.readyCount += 1
        self.notify_room()
        if self.readyCount == len(self.players):
            self.distribute_roles()

    def choose_characters(self):
        char_cards = random.sample(characters.all_characters(), len(self.players)*2)
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
        self.initial_players = len(self.players)
        self.choose_characters()

    def distribute_roles(self):
        available_roles: List[roles.Role] = []
        if len(self.players) == 3:
            available_roles = [
                roles.Vice('Elimina il Rinnegato 🦅, se non lo elimini tu elimina anche il Fuorilegge'),
                roles.Renegade('Elimina il Fuorilegge 🐺, se non lo elimini tu elimina anche il Vice'),
                roles.Outlaw('Elimina il Vice 🎖, se non lo elimini tu elimina anche il Rinnegato')
            ]
        elif len(self.players) >= 4:
            available_roles = [roles.Sheriff(), roles.Renegade(), roles.Outlaw(), roles.Outlaw(), roles.Vice(), roles.Outlaw(), roles.Vice()]
            available_roles = available_roles[:len(self.players)]
        random.shuffle(available_roles)
        for i in range(len(self.players)):
            self.sio.emit('chat_message', room=self.name, data=f'{self.players[i].name} ha come personaggio {self.players[i].character.name}, la sua abilità speciale è: {self.players[i].character.desc}')
            self.players[i].set_role(available_roles[i])
            if isinstance(available_roles[i], roles.Sheriff) or (len(available_roles) == 3 and isinstance(available_roles[i], roles.Vice)):
                if isinstance(available_roles[i], roles.Sheriff):
                    self.sio.emit('chat_message', room=self.name, data=f'{self.players[i].name} È lo sceriffo')
                self.turn = i
            self.players[i].prepare()
            for k in range(self.players[i].max_lives):
                self.players[i].hand.append(self.deck.draw())
            self.players[i].notify_self()
        self.play_turn()

    def attack_others(self, attacker: players.Player):
        attacker.pending_action = players.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.readyCount = 0
        for p in self.players:
            if p != attacker:
                if p.get_banged(attacker=attacker):
                    self.waiting_for += 1
        if self.waiting_for == 0:
            attacker.pending_action = players.PendingAction.PLAY
            attacker.notify_self()

    def indian_others(self, attacker: players.Player):
        attacker.pending_action = players.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.readyCount = 0
        for p in self.players:
            if p != attacker:
                if p.get_indians(attacker=attacker):
                    self.waiting_for += 1
        if self.waiting_for == 0:
            attacker.pending_action = players.PendingAction.PLAY
            attacker.notify_self()

    def attack(self, attacker: players.Player, target_username:str):
        if self.players[self.players_map[target_username]].get_banged(attacker=attacker, double=isinstance(attacker.character, characters.SlabTheKiller)):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = players.PendingAction.WAIT
            attacker.notify_self()

    def duel(self, attacker: players.Player, target_username:str):
        if self.players[self.players_map[target_username]].get_dueled(attacker=attacker):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = players.PendingAction.WAIT
            attacker.notify_self()

    def emporio(self):
        self.available_cards = [self.deck.draw() for i in range(len(self.players))]
        self.players[self.turn].pending_action = players.PendingAction.CHOOSE
        self.players[self.turn].available_cards = self.available_cards
        self.players[self.turn].notify_self()

    def respond_emporio(self, player, i):
        player.hand.append(self.available_cards.pop(i))
        player.available_cards = []
        player.pending_action = players.PendingAction.WAIT
        player.notify_self()
        nextPlayer = self.players[(self.turn + (len(self.players)-len(self.available_cards))) % len(self.players)]
        if nextPlayer == self.players[self.turn]:
            self.players[self.turn].pending_action = players.PendingAction.PLAY
            self.players[self.turn].notify_self()
        else:
            nextPlayer.pending_action = players.PendingAction.CHOOSE
            nextPlayer.available_cards = self.available_cards
            nextPlayer.notify_self()

    def get_player_named(self, name:str):
        return self.players[self.players_map[name]]

    def responders_did_respond_resume_turn(self):
        self.readyCount += 1
        if self.readyCount == self.waiting_for:
            self.waiting_for = 0
            self.readyCount = 0
            self.players[self.turn].pending_action = players.PendingAction.PLAY
            self.players[self.turn].notify_self()

    def next_player(self):
        return self.players[(self.turn + 1) % len(self.players)]

    def play_turn(self):
        self.players[self.turn].play_turn()

    def next_turn(self):
        if len(self.players) > 0:
            self.turn = (self.turn + 1) % len(self.players)
            self.play_turn()

    def notify_scrap_pile(self):
        print('scrap')
        if self.deck.peek_scrap_pile():
            self.sio.emit('scrap', room=self.name, data=self.deck.peek_scrap_pile().__dict__)
        else:
            self.sio.emit('scrap', room=self.name, data=None)

    def handle_disconnect(self, player: players.Player):
        print(f'player {player.name} left the game {self.name}')
        self.player_death(player=player)
        if len(self.players) == 0:
            print(f'no players left in game {self.name}')
            return True
        else: return False

    def player_death(self, player: players.Player):
        print(player.attacker)
        if player.attacker and isinstance(player.attacker, roles.Sheriff) and isinstance(player.role, roles.Vice):
            for i in range(len(player.attacker.hand)):
                self.deck.scrap(player.attacker.hand.pop())
            for i in range(len(player.attacker.equipment)):
                self.deck.scrap(player.attacker.equipment.pop())
            player.attacker.notify_self()
        elif player.attacker and (isinstance(player.role, roles.Outlaw) or self.initial_players == 3):
            for i in range(3):
                player.attacker.hand.append(self.deck.draw())
            player.attacker.notify_self()
        print(f'player {player.name} died')
        if (self.waiting_for > 0):
            self.responders_did_respond_resume_turn()
        vulture = [p for p in self.players if isinstance(p.character, characters.VultureSam)]
        if len(vulture) == 0:
            for i in range(len(player.hand)):
                self.deck.scrap(player.hand.pop())
            for i in range(len(player.equipment)):
                self.deck.scrap(player.equipment.pop())
        else:
            for i in range(len(player.hand)):
                vulture[0].hand.append(player.hand.pop())
            for i in range(len(player.equipment)):
                vulture[0].hand.append(player.equipment.pop())
        index = self.players.index(player)
        died_in_his_turn = self.started and index == self.turn
        if self.started and index <= self.turn:
            self.turn -= 1
        self.players.pop(index)
        self.notify_room()
        self.sio.emit('chat_message', room=self.name, data=f'{player.name} è morto.')
        if self.started:
            self.sio.emit('chat_message', room=self.name, data=f'{player.name} era {player.role.name}!')
        for p in self.players:
            p.notify_self()
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        if self.started:
            print('Check win status')
            attacker_role = None
            if player.attacker:
                attacker_role = player.attacker.role
            winners = [p for p in self.players if p.role != None and p.role.on_player_death(self.players, initial_players=self.initial_players, dead_role=player.role, attacker_role=attacker_role)]
            if len(winners) > 0:
                print('WE HAVE A WINNER')
                for p in self.players:
                    p.win_status = p in winners
                    p.notify_self()
                return

        if died_in_his_turn:
            self.next_turn()

    def get_visible_players(self, player: players.Player):
        i = self.players.index(player)
        sight = player.get_sight()
        return [{
            'name': self.players[j].name,
            'dist': min(abs(i - j), (i+ abs(j-len(self.players))), (j+ abs(i-len(self.players)))) + self.players[j].get_visibility() - (player.get_sight(countWeapon=False)-1),
            'lives': self.players[j].lives,
            'max_lives': self.players[j].max_lives,
            'is_sheriff': isinstance(self.players[j].role, roles.Sheriff),
        } for j in range(len(self.players)) if i != j]

    def notify_all(self):
        if self.started:
            data = [{
                'name': p.name,
                'ncards': len(p.hand),
                'equipment': [e.__dict__ for e in p.equipment],
                'lives': p.lives,
                'max_lives': p.max_lives,
                'is_sheriff': isinstance(p.role, roles.Sheriff),
                'is_my_turn': p.is_my_turn,
                'pending_action': p.pending_action,
                'character': p.character.__dict__ if p.character else None,
                'icon': p.role.icon if self.initial_players == 3 and p.role else '🤠'
            } for p in self.players]
            self.sio.emit('players_update', room=self.name, data=data)

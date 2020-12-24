
from typing import List, Set, Dict, Tuple, Optional
import random
import socketio
import eventlet

import bang.players as pl
import bang.characters as characters
from bang.deck import Deck
import bang.roles as roles
import bang.expansions.fistful_of_cards.card_events as ce
import bang.expansions.high_noon.card_events as ceh

class Game:
    def __init__(self, name, sio:socketio):
        super().__init__()
        self.sio = sio
        self.name = name
        self.players: List[pl.Player] = []
        self.spectators: List[pl.Player] = []
        self.deck: Deck = None
        self.started = False
        self.turn = 0
        self.readyCount = 0
        self.waiting_for = 0
        self.initial_players = 0
        self.password = ''
        self.expansions = []
        self.available_expansions = ['dodge_city', 'fistful_of_cards', 'high_noon']
        self.shutting_down = False
        self.is_competitive = False
        self.disconnect_bot = True
        self.player_bangs = 0
        self.is_russian_roulette_on = False
        self.dalton_on = False
        self.bot_speed = 1.5
        self.incremental_turn = 0
        self.did_resuscitate_deadman = False

    def notify_room(self, sid=None):
        if len([p for p in self.players if p.character == None]) != 0 or sid:
            self.sio.emit('room', room=self.name if not sid else sid, data={
                'name': self.name,
                'started': self.started,
                'players': [{'name':p.name, 'ready': p.character != None} for p in self.players],
                'password': self.password,
                'is_competitive': self.is_competitive,
                'disconnect_bot': self.disconnect_bot,
                'expansions': self.expansions,
                'available_expansions': self.available_expansions
            })

    def toggle_expansion(self, expansion_name):
        if not self.started:
            print('toggling', expansion_name)
            if expansion_name in self.expansions:
                self.expansions.remove(expansion_name)
            else:
                self.expansions.append(expansion_name)
            self.notify_room()

    def toggle_competitive(self):
        self.is_competitive = not self.is_competitive
        self.notify_room()

    def toggle_disconnect_bot(self):
        self.disconnect_bot = not self.disconnect_bot
        self.notify_room()

    def add_player(self, player: pl.Player):
        if player.is_bot and len(self.players) >= 8:
            return
        if player in self.players or len(self.players) >= 10:
            return
        if len(self.players) > 7:
            if 'dodge_city' not in self.expansions:
                self.expansions.append('dodge_city')
        player.join_game(self)
        self.players.append(player)
        print(f'Added player {player.name} to game')
        self.notify_room()
        self.sio.emit('chat_message', room=self.name, data=f'_joined|{player.name}')

    def set_private(self):
        if self.password == '':
            self.password = ''.join(random.choice("AEIOUJKZT123456789") for x in range(6))
            print(self.name, 'is now private pwd', self.password)
        else:
            self.password = ''
        self.notify_room()

    def notify_character_selection(self):
        self.notify_room()
        if len([p for p in self.players if p.character == None]) == 0:
            for i in range(len(self.players)):
                print(self.name)
                print(self.players[i].name)
                print(self.players[i].character)
                self.sio.emit('chat_message', room=self.name, data=f'_choose_character|{self.players[i].name}|{self.players[i].character.name}|{self.players[i].character.desc}|{self.players[i].character.desc_eng}')
                self.players[i].prepare()
                for k in range(self.players[i].max_lives):
                    self.players[i].hand.append(self.deck.draw())
                self.players[i].notify_self()
            current_roles = [type(x.role).__name__ for x in self.players]
            random.shuffle(current_roles)
            current_roles = str({x:current_roles.count(x) for x in current_roles}).replace('{','').replace('}','')
            self.sio.emit('chat_message', room=self.name, data=f'_allroles|{current_roles}')
            self.play_turn()

    def choose_characters(self):
        char_cards = random.sample(characters.all_characters(self.expansions), len(self.players)*2)
        for i in range(len(self.players)):
            self.players[i].set_available_character(char_cards[i * 2 : i * 2 + 2])

    def start_game(self):
        print('GAME IS STARING')
        if self.started:
            return
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        self.sio.emit('chat_message', room=self.name, data=f'_starting')
        self.sio.emit('start', room=self.name)
        self.started = True
        self.deck = Deck(self)
        self.initial_players = len(self.players)
        self.distribute_roles()
        self.choose_characters()

    def distribute_roles(self):
        available_roles: List[roles.Role] = []
        if len(self.players) == 3:
            available_roles = [
                roles.Vice('Elimina il Rinnegato 🦅, se non lo elimini tu elimina anche il Fuorilegge', 'Kill the Renegade 🦅, if you are not the one who kills him then kill the Outlaw!'),
                roles.Renegade('Elimina il Fuorilegge 🐺, se non lo elimini tu elimina anche il Vice', 'Kill the Outlaw 🐺, if you are not the one who kills him then kill the Vice!'),
                roles.Outlaw('Elimina il Vice 🎖, se non lo elimini tu elimina anche il Rinnegato', 'Kill the Vice 🎖, if you are not the one who kills him then kill the Renegade!')
            ]
        elif len(self.players) >= 4:
            available_roles = [roles.Sheriff(), roles.Renegade(), roles.Outlaw(), roles.Outlaw(), roles.Vice(), roles.Outlaw(), roles.Vice(), roles.Renegade(), roles.Outlaw(), roles.Vice(), roles.Outlaw()]
            available_roles = available_roles[:len(self.players)]
        else:
            available_roles = [roles.Renegade(), roles.Renegade()]
        random.shuffle(available_roles)
        for i in range(len(self.players)):
            self.players[i].set_role(available_roles[i])
            if isinstance(available_roles[i], roles.Sheriff) or (len(available_roles) == 3 and isinstance(available_roles[i], roles.Vice)):
                if isinstance(available_roles[i], roles.Sheriff):
                    self.sio.emit('chat_message', room=self.name, data=f'_sheriff|{self.players[i].name}')
                self.turn = i
            self.players[i].notify_self()
        self.notify_event_card()

    def attack_others(self, attacker: pl.Player):
        attacker.pending_action = pl.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.readyCount = 0
        for p in self.get_alive_players():
            if p != attacker:
                if p.get_banged(attacker=attacker):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = pl.PendingAction.PLAY
            attacker.notify_self()

    def indian_others(self, attacker: pl.Player):
        attacker.pending_action = pl.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.readyCount = 0
        for p in self.get_alive_players():
            if p != attacker:
                if p.get_indians(attacker=attacker):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = pl.PendingAction.PLAY
            attacker.notify_self()

    def attack(self, attacker: pl.Player, target_username:str, double:bool=False):
        if self.get_player_named(target_username).get_banged(attacker=attacker, double=double):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def rimbalzo(self, attacker: pl.Player, target_username:str, card_index:int):
        if self.get_player_named(target_username).get_banged(attacker=attacker, no_dmg=True, card_index=card_index):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def duel(self, attacker: pl.Player, target_username:str):
        if self.get_player_named(target_username).get_dueled(attacker=attacker):
            self.readyCount = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def emporio(self):
        pls = self.get_alive_players()
        self.available_cards = [self.deck.draw(True) for i in range(len(pls))]
        self.players[self.turn].pending_action = pl.PendingAction.CHOOSE
        self.players[self.turn].choose_text = 'choose_card_to_get'
        self.players[self.turn].available_cards = self.available_cards
        self.players[self.turn].notify_self()

    def respond_emporio(self, player, i):
        player.hand.append(self.available_cards.pop(i))
        player.available_cards = []
        player.pending_action = pl.PendingAction.WAIT
        player.notify_self()
        pls = self.get_alive_players()
        nextPlayer = pls[(pls.index(self.players[self.turn])+(len(pls)-len(self.available_cards))) % len(pls)]
        if nextPlayer == self.players[self.turn]:
            self.players[self.turn].pending_action = pl.PendingAction.PLAY
            self.players[self.turn].notify_self()
        else:
            nextPlayer.pending_action = pl.PendingAction.CHOOSE
            nextPlayer.choose_text = 'choose_card_to_get'
            nextPlayer.available_cards = self.available_cards
            nextPlayer.notify_self()

    def get_player_named(self, name:str):
        return self.players[self.players_map[name]]

    def responders_did_respond_resume_turn(self, did_lose=False):
        print('did_lose', did_lose)
        if self.player_bangs > 0 and self.check_event(ce.PerUnPugnoDiCarte):
            self.player_bangs -= 1
            if self.player_bangs > 1:
                print('bang again')
                if self.players[self.turn].get_banged(self.deck.event_cards[0]):
                    self.players[self.turn].notify_self()
                else:
                    self.responders_did_respond_resume_turn()
            else:
                print('ok play turn now')
                self.player_bangs = 0
                self.players[self.turn].play_turn()
        elif self.is_russian_roulette_on and self.check_event(ce.RouletteRussa):
            if did_lose:
                print('stop roulette')
                self.players[(self.turn+self.player_bangs) % len(self.players)].lives -= 1
                self.players[(self.turn+self.player_bangs) % len(self.players)].notify_self()
                self.is_russian_roulette_on = False
                self.players[self.turn].play_turn()
            else:
                self.player_bangs += 1
                print(f'next in line {self.players[(self.turn+self.player_bangs) % len(self.players)].name}')
                if self.players[(self.turn+self.player_bangs) % len(self.players)].get_banged(self.deck.event_cards[0]):
                    self.players[(self.turn+self.player_bangs) % len(self.players)].notify_self()
                else:
                    self.responders_did_respond_resume_turn(did_lose=True)
        else:
            self.readyCount += 1
            if self.readyCount == self.waiting_for:
                self.waiting_for = 0
                self.readyCount = 0
                self.players[self.turn].pending_action = pl.PendingAction.PLAY
                self.players[self.turn].notify_self()

    def next_player(self):
        pls = self.get_alive_players()
        return pls[(pls.index(self.players[self.turn]) + 1) % len(pls)]

    def play_turn(self):
        self.incremental_turn += 1
        if self.players[self.turn].is_dead:
            pl = sorted(self.get_dead_players(), key=lambda x:x.death_turn)[0]
            if self.check_event(ce.DeadMan) and not self.did_resuscitate_deadman and pl != self.players[self.turn]:
                print(f'{self.players[self.turn]} is dead, revive')
                self.did_resuscitate_deadman = True
                pl.is_dead = False
                pl.is_ghost = False
                pl.lives = 2
                pl.hand.append(self.deck.draw())
                pl.hand.append(self.deck.draw())
                pl.notify_self()
            elif self.check_event(ceh.CittaFantasma):
                print(f'{self.players[self.turn]} is dead, event ghost')
                self.players[self.turn].is_ghost = True
            else:
                print(f'{self.players[self.turn]} is dead, next turn')
                return self.next_turn()
        self.player_bangs = 0
        if isinstance(self.players[self.turn].role, roles.Sheriff):
            self.deck.flip_event()
            if len(self.deck.event_cards) > 0 and self.deck.event_cards[0] != None:
                print(f'flip new event {self.deck.event_cards[0].name}')
            if self.check_event(ce.DeadMan):
                self.did_resuscitate_deadman = False
            elif self.check_event(ce.RouletteRussa):
                self.is_russian_roulette_on = True
                if self.players[self.turn].get_banged(self.deck.event_cards[0]):
                    self.players[self.turn].notify_self()
                else:
                    self.responders_did_respond_resume_turn(did_lose=True)
                return
            elif self.check_event(ceh.IlDottore):
                most_hurt = [p.lives for p in self.players if p.lives > 0 and p.max_lives > p.lives]
                if len(most_hurt) > 0:
                    hurt_players = [p for p in self.players if p.lives == min(most_hurt)]
                    for p in hurt_players:
                        p.lives += 1
                        self.sio.emit('chat_message', room=self.name, data=f'_doctor_heal|{p.name}')
                        p.notify_self()
            elif self.check_event(ceh.IDalton):
                self.waiting_for = 0
                self.readyCount = 0
                self.dalton_on = True
                for p in self.players:
                    if p.get_dalton():
                        self.waiting_for += 1
                        p.notify_self()
                if self.waiting_for != 0:
                    return
                self.dalton_on = False

        if self.check_event(ce.PerUnPugnoDiCarte) and len(self.players[self.turn].hand) > 0:
            self.player_bangs = len(self.players[self.turn].hand)
            if self.players[self.turn].get_banged(self.deck.event_cards[0]):
                self.players[self.turn].notify_self()
            else:
                self.responders_did_respond_resume_turn()
        else:
            print(f'notifying {self.players[self.turn].name} about his turn')
            self.players[self.turn].play_turn()

    def next_turn(self):
        if self.shutting_down: return
        print(f'{self.players[self.turn].name} invoked next turn')
        pls = self.get_alive_players()
        if len(pls) > 0:
            if self.check_event(ceh.CorsaAllOro):
                self.turn = (self.turn - 1) % len(self.players)
            else:
                self.turn = (self.turn + 1) % len(self.players)
            self.play_turn()

    def notify_event_card(self):
        if len(self.deck.event_cards) > 0:
            if self.deck.event_cards[0] != None:
                self.sio.emit('event_card', room=self.name, data=self.deck.event_cards[0].__dict__)
            else:
                self.sio.emit('event_card', room=self.name, data=None)

    def notify_scrap_pile(self):
        print('scrap')
        if self.deck.peek_scrap_pile():
            self.sio.emit('scrap', room=self.name, data=self.deck.peek_scrap_pile().__dict__)
        else:
            self.sio.emit('scrap', room=self.name, data=None)

    def handle_disconnect(self, player: pl.Player):
        print(f'player {player.name} left the game {self.name}')
        if player in self.spectators:
            self.spectators.remove(player)
            return
        if self.disconnect_bot and self.started:
            player.is_bot = True
            eventlet.sleep(15) # he may reconnect
            player.notify_self()
        else:
            self.player_death(player=player, disconnected=True)
        # else:
        #     player.lives = 0
            # self.players.remove(player)
        if len([p for p in self.players if not p.is_bot]) == 0:
            print(f'no players left in game {self.name}')
            self.shutting_down = True
            self.players = []
            self.spectators = []
            self.deck = None
            return True
        else: return False

    def player_death(self, player: pl.Player, disconnected=False):
        if not player in self.players or player.is_ghost: return
        import bang.expansions.dodge_city.characters as chd
        print(player.attacker)
        if player.attacker and player.attacker in self.players and isinstance(player.attacker.role, roles.Sheriff) and isinstance(player.role, roles.Vice):
            for i in range(len(player.attacker.hand)):
                self.deck.scrap(player.attacker.hand.pop(), True)
            for i in range(len(player.attacker.equipment)):
                self.deck.scrap(player.attacker.equipment.pop(), True)
            player.attacker.notify_self()
        elif player.attacker and player.attacker in self.players and (isinstance(player.role, roles.Outlaw) or self.initial_players == 3):
            for i in range(3):
                player.attacker.hand.append(self.deck.draw(True))
            player.attacker.notify_self()
        print(f'player {player.name} died')
        if (self.waiting_for > 0):
            self.responders_did_respond_resume_turn()

        if player.is_dead: return
        if not self.started:
            self.players.remove(player)
        elif disconnected:
            index = self.players.index(player)
            if self.started and index <= self.turn:
                self.turn -= 1
            self.players.remove(player)
            self.players_map = {c.name: i for i, c in enumerate(self.players)}
        player.lives = 0
        player.is_dead = True
        player.death_turn = self.incremental_turn

        # corpse = self.players.pop(index)
        corpse = player
        # if not disconnected:
        #     self.dead_players.append(corpse)
        self.notify_room()
        self.sio.emit('chat_message', room=self.name, data=f'_died|{player.name}')
        if self.started:
            self.sio.emit('chat_message', room=self.name, data=f'_died_role|{player.name}|{player.role.name}')
        for p in self.players:
            if not p.is_bot:
                p.notify_self()
        # self.players_map = {c.name: i for i, c in enumerate(self.players)}
        if self.started:
            print('Check win status')
            attacker_role = None
            if player.attacker and player.attacker in self.players:
                attacker_role = player.attacker.role
            winners = [p for p in self.players if p.role != None and p.role.on_player_death(self.get_alive_players(), initial_players=self.initial_players, dead_role=player.role, attacker_role=attacker_role)]
            if len(winners) > 0:
                print('WE HAVE A WINNER')
                for p in self.get_alive_players():
                    p.win_status = p in winners
                    self.sio.emit('chat_message', room=self.name, data=f'_won|{p.name}')
                    p.notify_self()
                eventlet.sleep(5.0)
                return self.reset()

            vulture = [p for p in self.get_alive_players() if p.character.check(self, characters.VultureSam)]
            if len(vulture) == 0:
                for i in range(len(player.hand)):
                    self.deck.scrap(player.hand.pop(), True)
                for i in range(len(player.equipment)):
                    self.deck.scrap(player.equipment.pop(), True)
            elif len(vulture) == 2:
                for i in range(len(player.hand)):
                    vulture[i%2].hand.append(player.hand.pop())
                for i in range(len(player.equipment)):
                    vulture[i%2].hand.append(player.equipment.pop())
                vulture[0].notify_self()
                vulture[1].notify_self()
            else:
                for i in range(len(player.hand)):
                    vulture[0].hand.append(player.hand.pop())
                for i in range(len(player.equipment)):
                    vulture[0].hand.append(player.equipment.pop())
                vulture[0].notify_self()

            #se Vulture Sam è uno sceriffo e ha appena ucciso il suo Vice, deve scartare le carte che ha pescato con la sua abilità
            if player.attacker and player.attacker in self.get_alive_players() and isinstance(player.attacker.role, roles.Sheriff) and isinstance(player.role, roles.Vice):
                for i in range(len(player.attacker.hand)):
                    self.deck.scrap(player.attacker.hand.pop(), True)
                player.attacker.notify_self()

            greg = [p for p in self.get_alive_players() if p.character.check(self, chd.GregDigger)]
            if len(greg) > 0:
                greg[0].lives = min(greg[0].lives+2, greg[0].max_lives)
            herb = [p for p in self.get_alive_players() if p.character.check(self, chd.HerbHunter)]
            if len(herb) > 0:
                herb[0].hand.append(self.deck.draw(True))
                herb[0].hand.append(self.deck.draw(True))
                herb[0].notify_self()
        
        if corpse.is_my_turn:
            self.next_turn()

    def reset(self):
        print('resetting lobby')
        self.players.extend(self.spectators)
        self.spectators = []
        self.players = [p for p in self.players if not p.is_bot]
        print(self.players)
        self.started = False
        self.waiting_for = 0
        self.incremental_turn = 0
        for p in self.players:
            p.reset()
            p.notify_self()
        eventlet.sleep(0.5)
        self.notify_room()

    def check_event(self, ev):
        if self.deck == None or len(self.deck.event_cards) == 0: return False
        return isinstance(self.deck.event_cards[0], ev)

    def get_visible_players(self, player: pl.Player):
        pls = self.get_alive_players()
        if len(pls) == 0 or player not in pls: return []
        i = pls.index(player)
        sight = player.get_sight()
        mindist = 99 if not self.check_event(ce.Agguato) else 1
        return [{
            'name': pls[j].name,
            'dist': min([abs(i - j), (i+ abs(j-len(pls))), (j+ abs(i-len(pls))), mindist]) + pls[j].get_visibility() - (player.get_sight(countWeapon=False)-1),
            'lives': pls[j].lives,
            'max_lives': pls[j].max_lives,
            'is_sheriff': isinstance(pls[j].role, roles.Sheriff),
            'cards': len(pls[j].hand)+len(pls[j].equipment),
            'is_ghost': pls[j].is_ghost,
        } for j in range(len(pls)) if i != j]

    def get_alive_players(self):
        return [p for p in self.players if not p.is_dead or p.is_ghost]

    def get_dead_players(self):
        return [p for p in self.players if p.is_dead]

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
                'real_character': p.real_character.__dict__ if p.real_character else None,
                'icon': p.role.icon if self.initial_players == 3 and p.role else '🤠',
                'is_ghost': p.is_ghost,
            } for p in self.get_alive_players()]
            self.sio.emit('players_update', room=self.name, data=data)

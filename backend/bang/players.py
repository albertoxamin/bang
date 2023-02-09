from __future__ import annotations
from enum import IntEnum
import json
from random import random, randrange, sample, uniform
import socketio
import bang.deck as deck
import bang.roles as r
import bang.cards as cs
import bang.expansions.dodge_city.cards as csd
import bang.characters as chars
import bang.expansions.dodge_city.characters as chd
import bang.expansions.fistful_of_cards.card_events as ce
import bang.expansions.high_noon.card_events as ceh
import bang.expansions.gold_rush.shop_cards as grc
import bang.expansions.gold_rush.characters as grch
import bang.expansions.the_valley_of_shadows.cards as tvosc
import bang.expansions.the_valley_of_shadows.characters as tvosch
from typing import List, TYPE_CHECKING
from metrics import Metrics
from globals import G
import sys

if TYPE_CHECKING:
    from bang.game import Game

robot_pictures = [
    'https://i.imgur.com/40rAFIb.jpg',
    'https://i.imgur.com/gG77VRR.jpg',
    'https://i.imgur.com/l2DTQeH.jpg',
    'https://i.imgur.com/aPM2gix.jpg',
    'https://i.imgur.com/ep5EB8c.jpg',
    'https://i.imgur.com/qsOWIsf.jpg',
    'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/325/robot_1f916.png',
    'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/openmoji/338/robot_1f916.png',
    'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/microsoft/319/robot_1f916.png',
    'https://i.imgur.com/0plPBZR.png',
    'https://i.imgur.com/DScxoSX.png',
    'https://i.imgur.com/YzPQChj.png',
    'https://i.imgur.com/v3BvnX4.png',
    'https://i.imgur.com/1XHsE9f.png',
    'https://i.imgur.com/q0CrH2c.png',
    'https://i.imgur.com/Z5vXgd4.png',
]

class PendingAction(IntEnum):
    PICK = 0
    DRAW = 1
    PLAY = 2
    RESPOND = 3
    WAIT = 4
    CHOOSE = 5

class Player:
    def is_admin(self):
        return self.discord_id in {'244893980960096266', '539795574019457034'}

    def _get_avatar(self):
        import requests
        headers = {
            'Authorization': 'Bearer ' + self.discord_token,
        }
        r = requests.get('https://discordapp.com/api/users/@me', headers=headers)
        if r.status_code == 200:
            res = r.json()
            print(res)
            if res["avatar"] is None:
                self.avatar = robot_pictures[randrange(len(robot_pictures))]
            else:
                self.avatar = f'https://cdn.discordapp.com/avatars/{res["id"]}/{res["avatar"]}.png'
            if self.game:
                G.sio.emit('chat_message', room=self.game.name, data=f'_change_username|{self.name}|{res["username"]}')
            self.name = res['username']
            self.discord_id = res['id']
            if self.is_admin():
                if self.game: self.game.feature_flags()
                G.sio.emit('chat_message', room=self.sid, data={'color':'green', 'text':'(you are admin)'})
            if self.game:
                self.game.notify_room()
                G.sio.emit('me', data=self.name, room=self.sid)
        else:
            print('error getting avatar', r.status_code, r.text)
            print(r)

    def __init__(self, name, sid, bot=False, discord_token=None):
        super().__init__()
        self.name = name
        self.sid = sid
        self.is_bot = bot
        self.discord_token = discord_token
        self.discord_id = None
        self.avatar = ''
        if self.is_bot:
            self.avatar = robot_pictures[randrange(len(robot_pictures))]
        if self.discord_token:
            G.sio.start_background_task(self._get_avatar)
        self.game: Game = None
        self.reset()

    def reset(self):
        self.hand: List[cs.Card] = []
        self.equipment: List[cs.Card] = []
        self.role: r.Role = None
        self.character: chars.Character = None
        self.real_character: chars.Character = None
        self.is_using_checchino = False
        self.lives = 0
        self.max_lives = 0
        self.is_my_turn = False
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.can_play_ranch = True
        self.is_playing_ranch = False
        self.pending_action: PendingAction = None
        self.available_characters: List[chars.Character] = []
        self.was_shot = False
        self.on_pick_cb = None
        self.on_failed_response_cb = None
        self.event_type: str = None
        self.expected_response = []
        self.attacking_card = None
        self.attacker: Player = None
        self.target_p: str = None
        self.is_drawing = False
        self.special_use_count = 0
        self.rissa_targets = []
        self.committed_suit_manette = None
        self.not_chosen_character = None
        try:
            # pylint: disable=no-member
            del self.win_status
        except:
            pass
        self.mancato_needed = 0
        self.molly_discarded_cards = 0
        self.is_dead = False
        self.is_ghost = False
        self.death_turn = 0
        self.noStar = False
        self.can_play_vendetta = True
        self.can_play_again_don_bell = True
        self.is_giving_life = False
        self.choose_text = 'choose_card_to_get'
        self.using_rimbalzo = 0 # 0 no, 1 scegli giocatore, 2 scegli carta
        self.bang_used = 0
        self.gold_nuggets = 0
        self.gold_rush_equipment: List[grc.ShopCard] = []
        self.was_player = False
        self.setaccio_count = 0
        self.choose_action = ''

    def join_game(self, game):
        self.game = game
        print(f'I {self.name} joined {self.game}')

    def disconnect(self):
        if self.is_admin() and self.game.debug and self.game.started and getattr(sys, 'gettrace', None)(): return False
        return self.game.handle_disconnect(self)

    def set_role(self, role: r.Role):
        self.role = role
        print(f'{self.name}: I am a {role.name}, my goal is "{role.goal}"')
        G.sio.emit('role', room=self.sid, data=json.dumps(
            role, default=lambda o: o.__dict__))

    def set_character(self, character: str):
        print(self.available_characters, character)
        if self.character is None:
            try:
                self.character = next(x for x in self.available_characters if x.name == character)
            except:
                # fix for wrong character encoding in the first part of some characters like Jose delgrado
                self.character = next(x for x in self.available_characters if x.name.split()[1] == character.split()[1])
            if 'high_noon' in self.game.expansions:
                # questo viene utilizzato per la carta nuova identità
                self.not_chosen_character = next(x for x in self.available_characters if x.name != character)
            else:
                self.not_chosen_character = None
            self.real_character = self.character
            self.available_characters = []
            print(f'{self.name}: I chose character {self.character.name}')
            G.sio.emit('chat_message', room=self.game.name,
                        data=f'_did_choose_character|{self.name}')
            self.game.notify_character_selection()
        elif self.real_character and isinstance(self.real_character, chd.VeraCuster):
            self.character = next(
                x for x in self.available_characters if x.name == character)
            self.available_characters = []
            G.sio.emit('chat_message', room=self.game.name,
                        data=f'_did_choose_character|{self.name}')
            self.pending_action = PendingAction.DRAW
            self.notify_self()

    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
        self.hand = []
        self.equipment = []
        self.pending_action = PendingAction.WAIT
        self.noStar = (self.game.initial_players == 3)

    def set_available_character(self, available):
        self.available_characters = available
        print(f'{self.name}: I have to choose between {available}')
        if not self.is_bot:
            G.sio.emit('characters', room=self.sid, data=json.dumps(
                available, default=lambda o: o.__dict__))
        else:
            char_name = available[randrange(0, len(available))].name
            self.game.rpc_log.append(f'{self.name};set_character;{char_name}')
            self.set_character(char_name)

    def notify_card(self, player, card, message=''):
        try:
            card = card.__dict__
        except:
            pass
        mess = {
            'player': player.name,
            'card': card,
            'message':message
        }
        print('notifying card')
        G.sio.emit('notify_card', room=self.sid, data=mess)

    def notify_self(self):
        if any((True for c in self.equipment if isinstance(c, tvosc.Fantasma))):
            self.is_ghost = True
        elif self.is_ghost and self.is_my_turn and not self.game.check_event(ceh.CittaFantasma):
            self.end_turn(forced=True)
        elif self.is_ghost and not self.game.check_event(ceh.CittaFantasma):
            self.is_ghost = False
            for i in range(len(self.hand)):
                self.game.deck.scrap(self.hand.pop(), True)
            for i in range(len(self.equipment)):
                self.game.deck.scrap(self.equipment.pop(), True)
        if self.is_ghost: self.lives = 0
        if self.pending_action == PendingAction.DRAW and self.game.check_event(ce.Peyote):
            self.available_cards = [{
                'icon': '🔴',
                'noDesc': True
            },{
                'icon': '⚫',
                'noDesc': True
            }]
            self.is_drawing = True
            self.choose_text = 'choose_guess'
            self.pending_action = PendingAction.CHOOSE
        elif self.can_play_ranch and self.pending_action == PendingAction.PLAY and self.game.check_event(ce.Ranch):
            self.can_play_ranch = False
            self.available_cards = [c for c in self.hand]
            self.discarded_cards = []
            self.available_cards.append({'icon': '✅','noDesc': True})
            self.is_playing_ranch = True
            self.choose_text = 'choose_ranch'
            self.pending_action = PendingAction.CHOOSE
        elif self.character and self.character.check(self.game, chars.SuzyLafayette) and self.lives > 0 and len(self.hand) == 0 and ( not self.is_my_turn or self.pending_action == PendingAction.PLAY):
            self.game.deck.draw(True, player=self)
        if self.lives <= 0 and self.max_lives > 0 and not self.is_dead:
            print('dying, attacker', self.attacker)
            if self.gold_nuggets >= 2 and any((isinstance(c, grc.Zaino) for c in self.gold_rush_equipment)):
                for i in range(len(self.gold_rush_equipment)):
                    if isinstance(self.gold_rush_equipment[i], grc.Zaino):
                        self.gold_rush_equipment[i].play_card(self, None)
                        return # play card will notify the player
            if self.character.check(self.game, chars.SidKetchum) and len(self.hand) > 1 and self.lives == 0:
                if self.game.players[self.game.turn] != self:
                    self.game.players[self.game.turn].pending_action = PendingAction.WAIT
                    self.game.players[self.game.turn].notify_self()
                self.scrapped_cards = 0
                self.previous_pending_action = self.pending_action
                self.pending_action = PendingAction.CHOOSE
                self.choose_text = 'choose_sid_scrap'
                self.available_cards = self.hand
                self.lives += 1
        
        ser = self.__dict__.copy()
        ser.pop('game')
        ser.pop('sid')
        ser.pop('on_pick_cb')
        ser.pop('discord_token')
        ser.pop('on_failed_response_cb')
        ser.pop('attacker')
        ser.pop('rissa_targets')
        if self.attacker:
            ser['attacker'] = self.attacker.name
        ser['sight'] = self.get_sight()
        ser['sight_extra'] = self.get_sight(False) -1
        ser['can_gold_rush_discard'] = any((p != self and any((e.number <= self.gold_nuggets + 1 for e in p.gold_rush_equipment)) for p in self.game.get_alive_players()))
        if self.character:
            ser['gold_rush_discount'] = 1 if self.character.check(self.game, grch.PrettyLuzena) and self.special_use_count < 1 else 0
        ser['lives'] = max(ser['lives'], 0)

        if self.lives <= 0 and self.max_lives > 0 and not self.is_dead:
            self.pending_action = PendingAction.WAIT
            ser['hand'] = []
            ser['equipment'] = []
            G.sio.emit('self', room=self.sid, data=json.dumps(ser, default=lambda o: o.__dict__))
            self.game.player_death(self)
        if self.game and self.game.started: # falso quando un bot viene eliminato dalla partita
            G.sio.emit('self_vis', room=self.sid, data=json.dumps(self.game.get_visible_players(self), default=lambda o: o.__dict__))
            self.game.notify_all()
        G.sio.emit('self', room=self.sid, data=json.dumps(ser, default=lambda o: o.__dict__))

    def bot_spin(self):
        while self.is_bot and self.game is not None and not self.game.shutting_down:
            G.sio.sleep(max(0.2, uniform(self.game.bot_speed/2-0.1, self.game.bot_speed)))
            if self.lives > 0 or self.is_ghost:
                self.bot_logic()

    def bot_logic(self):
        if self.game is None or self.game.shutting_down: return
        if self.pending_action is not None and self.pending_action != PendingAction.WAIT:
            # eventlet.sleep(uniform(self.game.bot_speed/2-0.1, self.game.bot_speed))
            pass
        else:
            return
        if self.pending_action == PendingAction.PICK:
            self.game.rpc_log.append(f'{self.name};pick;')
            self.pick()
        elif self.pending_action == PendingAction.DRAW:
            self.game.rpc_log.append(f'{self.name};draw;')
            self.draw('')
        elif self.pending_action == PendingAction.PLAY:
            non_blocked_cards = [card for card in self.hand if (not self.game.check_event(ceh.Manette) or card.suit == self.committed_suit_manette) and (not self.game.check_event(ce.IlGiudice) or not card.usable_next_turn) ]
            equippables = [c for c in non_blocked_cards if (c.is_equipment or c.usable_next_turn) and not isinstance(c, cs.Prigione) and not c.need_target and not any((type(c) == type(x) and not (c.is_weapon and c.must_be_used) for x in self.equipment))]
            misc = [c for c in non_blocked_cards if not c.need_target and (isinstance(c, cs.WellsFargo) or isinstance(c, cs.Indiani) or isinstance(c, cs.Gatling) or isinstance(c, cs.Diligenza) or isinstance(c, cs.Emporio) or ((isinstance(c, cs.Birra) and self.lives < self.max_lives or c.must_be_used) and not self.game.check_event(ceh.IlReverendo)) or (c.need_with and len(self.hand) > 1 and not (isinstance(c, csd.Whisky) and self.lives == self.max_lives)))
                    and not (not c.can_be_used_now and self.game.check_event(ce.IlGiudice)) and not c.is_equipment]
            need_target = [c for c in non_blocked_cards if c.need_target and c.can_be_used_now and not (c.need_with and len(self.hand) < 2) and not (type(c) == type(cs.Bang) and (self.game.check_event(ceh.Sermone) or (self.has_played_bang and (not any((isinstance(c, cs.Volcanic) for c in self.equipment)) or self.game.check_event(ce.Lazo))))) and not (isinstance(c, cs.Prigione) and self.game.check_event(ce.IlGiudice)) or isinstance(c, cs.Duello) or isinstance(c, cs.CatBalou) or isinstance(c, csd.Pugno)]
            green_cards = [c for c in self.equipment if not self.game.check_event(ce.Lazo) and not isinstance(c, cs.Mancato) and c.usable_next_turn and c.can_be_used_now]
            if self.game.debug:
                print(f'hand: {self.hand}')
                print(f'non_blocked: {non_blocked_cards}')
                print(f'equippables: {equippables}')
                print(f'misc: {misc}')
                print(f'need_target: {need_target}')
                print(f'green_cards: {green_cards}')
            if self.gold_nuggets > 0 and any((c.number <= self.gold_nuggets for c in self.game.deck.shop_cards)):
                for i in range(len(self.game.deck.shop_cards)):
                    if self.game.deck.shop_cards[i].number <= self.gold_nuggets:
                        self.game.rpc_log.append(f'{self.name};buy_gold_rush_card;{i}')
                        self.buy_gold_rush_card(i)
                        return
            if len(equippables) > 0 and not self.game.check_event(ce.IlGiudice):
                for c in equippables:
                    if isinstance(c, tvosc.Fantasma) and len(self.game.get_dead_players(include_ghosts=False)) == 0:
                        continue
                    if self.play_card(self.hand.index(c)):
                        return
            elif len(misc) > 0:
                for c in misc:
                    if c.need_with and len(self.hand) > 1 and self.play_card(self.hand.index(c), _with=sample([j for j in range(len(self.hand)) if j != self.hand.index(c)], 1)[0]):
                        return
                    elif self.play_card(self.hand.index(c)):
                        return
            elif len(need_target) > 0:
                for c in need_target:
                    _range = self.get_sight() if c.name == 'Bang!' or c.name == "Pepperbox" else c.range
                    others = [p for p in self.game.get_visible_players(self) if _range >= p['dist'] and not (isinstance(self.role, r.Vice) and p['is_sheriff'] and not c.must_be_used) and p['lives'] > 0 and not 
                    ((isinstance(c, cs.CatBalou) or isinstance(c, cs.Panico)) and p['cards'] == 0)
                     and not (p['is_sheriff'] and isinstance(c, cs.Prigione))]
                    if (isinstance(c, cs.Panico) or isinstance(c, cs.Panico))and len(self.equipment) > 0:
                        others.append({'name': self.name, 'is_sheriff': isinstance(self.role, r.Sheriff)})
                    if len(others) == 0 or c not in self.hand:
                        continue
                    target = others[randrange(0, len(others))]
                    if target['is_sheriff'] and isinstance(self.role, r.Renegade):
                        target = others[randrange(0, len(others))]
                    if not c.need_with:
                        if self.play_card(self.hand.index(c), against=target['name']):
                            return
                    elif len(self.hand) > 1:
                        if self.play_card(self.hand.index(c), against=target['name'], _with=sample([j for j in range(len(self.hand)) if j != self.hand.index(c)], 1)[0]):
                            return
            elif len(green_cards) > 0:
                for c in green_cards:
                    if not isinstance(c, cs.Mancato) and c.usable_next_turn and c.can_be_used_now:
                        if not c.need_target:
                            if self.play_card(len(self.hand)+self.equipment.index(c)):
                                return
                        else:
                            _range = self.get_sight() if c.name == "Pepperbox" else c.range
                            others = [p for p in self.game.get_visible_players(self) if _range >= p['dist'] and not (isinstance(self.role, r.Vice) and p['is_sheriff'])]
                            if len(others) == 0:
                                continue
                            target = others[randrange(0, len(others))]
                            if target['is_sheriff'] and isinstance(self.role, r.Renegade):
                                target = others[randrange(0, len(others))]
                            if self.play_card(len(self.hand)+self.equipment.index(c), against=target['name']):
                                return
                        break
            maxcards = self.lives if not self.character.check(self.game, chd.SeanMallory) else 10
            if maxcards == self.lives and any((isinstance(c, grc.Cinturone) for c in self.gold_rush_equipment)):
                maxcards = 8
            if len(self.hand) > maxcards:
                self.game.rpc_log.append(f'{self.name};scrap;{0}')
                self.scrap(0)
            else:
                self.game.rpc_log.append(f'{self.name};end_turn')
                self.end_turn()
        elif self.pending_action == PendingAction.RESPOND:
            did_respond = False
            for i in range(len(self.hand)):
                if self.hand[i].can_be_used_now and (self.hand[i].name in self.expected_response or self.character.check(self.game, chd.ElenaFuente)):
                    self.game.rpc_log.append(f'{self.name};respond;{i}')
                    self.respond(i)
                    did_respond = True
                    break
            for i in range(len(self.equipment)):
                if not self.game.check_event(ce.Lazo) and self.equipment[i].name in self.expected_response:
                    self.game.rpc_log.append(f'{self.name};respond;{len(self.hand)+i}')
                    self.respond(len(self.hand)+i)
                    did_respond = True
                    break
            if not did_respond:
                self.game.rpc_log.append(f'{self.name};respond;{-1}')
                self.respond(-1)
        elif self.pending_action == PendingAction.CHOOSE:
            if not self.target_p:
                card_index = randrange(0, len(self.available_cards))
                self.game.rpc_log.append(f'{self.name};choose;{card_index}')
                self.choose(card_index)
            else:
                target = self.game.get_player_named(self.target_p)
                if len(target.hand)+len(target.equipment) == 0:
                    self.pending_action = PendingAction.PLAY
                    self.notify_self()
                else:
                    try:
                        card_index = randrange(0, len(target.hand)+len(target.equipment))
                        self.choose(card_index)
                        self.game.rpc_log.append(f'{self.name};choose;{card_index}')
                    except:
                        self.choose(0)
                        self.game.rpc_log.append(f'{self.name};choose;{0}')


    def play_turn(self, can_play_vendetta = True, again = False):
        if ((self.lives == 0 or self.is_dead) and not self.is_ghost) or (self.is_ghost and any(isinstance(c, tvosc.Fantasma) for c in self.equipment) and self.game.check_event(ce.Lazo)):
            return self.end_turn(forced=True)
        self.scrapped_cards = 0
        self.setaccio_count = 0
        self.can_play_ranch = True
        self.is_playing_ranch = False
        self.can_play_vendetta = can_play_vendetta
        if not again:
            G.sio.emit('chat_message', room=self.game.name,
                          data=f'_turn|{self.name}')
            print(f'{self.name}: I was notified that it is my turn')
        self.was_shot = False
        self.attacker = None
        self.is_my_turn = True
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.special_use_count = 0
        self.bang_used = 0
        if self.game.check_event(ceh.MezzogiornoDiFuoco):
            self.lives -= 1
            if any((isinstance(c, grc.Talismano) for c in self.gold_rush_equipment)):
                self.gold_nuggets += 1
            if self.character.check(self.game, grch.SimeonPicos):
                self.gold_nuggets += 1
            if any((isinstance(c, grc.Stivali) for c in self.gold_rush_equipment)):
                self.game.deck.draw(True, player=self)
            if self.character.check(self.game, chars.BartCassidy) and self.lives > 0:
                self.game.deck.draw(True, player=self)
                G.sio.emit('chat_message', room=self.game.name, data=f'_special_bart_cassidy|{self.name}')
            self.heal_if_needed()
            if self.lives <= 0:
                return self.notify_self()

        #non è un elif perchè vera custer deve fare questo poi cambiare personaggio
        if self.game.check_event(ce.FratelliDiSangue) and self.lives > 1 and not self.is_giving_life and sum(p != self and p.lives < p.max_lives for p in self.game.get_alive_players()):
            self.available_cards = [{
                'name': p.name,
                'icon': p.role.icon if(self.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
                'alt_text': ''.join(['❤️']*p.lives)+''.join(['💀']*(p.max_lives-p.lives)),
                'avatar': p.avatar,
                'is_character': True,
                'is_player': True
            } for p in self.game.get_alive_players() if p != self and p.lives < p.max_lives]
            self.available_cards.append({'icon': '❌', 'noDesc': True})
            self.choose_text = 'choose_fratelli_di_sangue'
            self.pending_action = PendingAction.CHOOSE
            self.is_giving_life = True
        elif self.game.check_event(ceh.NuovaIdentita) and self.not_chosen_character is not None and not again:
            self.available_cards = [self.character, self.not_chosen_character]
            self.choose_text = 'choose_nuova_identita'
            self.pending_action = PendingAction.CHOOSE
        elif not self.game.check_event(ce.Lazo) and any((isinstance(c, cs.Dinamite) or isinstance(c, cs.Prigione) or isinstance(c, tvosc.SerpenteASonagli) for c in self.equipment)):
            self.is_giving_life = False
            self.pending_action = PendingAction.PICK
        else:
            self.is_giving_life = False
            if isinstance(self.real_character, chd.VeraCuster):
                self.set_available_character([p.character for p in self.game.get_alive_players() if p != self])
            else:
                self.pending_action = PendingAction.DRAW
        self.notify_self()

    def draw(self, pile):
        if self.is_my_turn and self.pending_action == PendingAction.PLAY and pile == 'event' and self.game.check_event(ce.Cecchino) and sum((c.name == cs.Bang(0,0).name for c in self.hand)) >= 2:
            self.is_using_checchino = True
            self.available_cards = [{
                'name': p['name'],
                'icon': p['role'].icon if(self.game.initial_players == 3) else '⭐️' if p['is_sheriff'] else '🤠',
                'alt_text': ''.join(['❤️']*p['lives'])+''.join(['💀']*(p['max_lives']-p['lives'])),
                'is_character': True,
                'is_player': True
            } for p in self.game.get_visible_players(self) if p['dist'] <= self.get_sight()]
            self.available_cards.append({'icon': '❌', 'noDesc': True})
            self.choose_text = 'choose_cecchino'
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        elif self.is_my_turn and self.pending_action == PendingAction.PLAY and pile == 'event' and self.game.check_event(ce.Rimbalzo) and any((c.name == cs.Bang(0,0).name for c in self.hand)):
            self.available_cards = [{
                'name': p.name,
                'icon': p.role.icon if(self.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
                'is_character': True,
                'avatar': p.avatar,
                'is_player': True
            } for p in self.game.get_alive_players() if len(p.equipment) > 0 and p != self]
            self.available_cards.append({'icon': '❌', 'noDesc': True})
            self.choose_text = 'choose_rimbalzo_player'
            self.pending_action = PendingAction.CHOOSE
            self.using_rimbalzo = 1
            self.notify_self()
        if self.pending_action != PendingAction.DRAW:
            return
        if pile == 'event' and self.lives < self.max_lives and self.game.check_event(ce.LiquoreForte):
            self.lives += 1
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.character.check(self.game, chars.KitCarlson) and not self.is_ghost:
            self.is_drawing = True
            self.available_cards = [self.game.deck.draw() for i in range(3)]
            self.choose_text = 'choose_card_to_get'
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        elif self.character.check(self.game, grch.DutchWill) and not self.is_ghost:
            self.is_drawing = True
            self.available_cards = [self.game.deck.draw() for i in range(2)]
            self.choose_text = 'choose_card_to_get'
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        elif self.character.check(self.game, chd.PatBrennan) and type(pile) == str and pile != self.name and pile in self.game.players_map and len(self.game.get_player_named(pile).equipment) > 0:
            self.is_drawing = True
            self.available_cards = self.game.get_player_named(pile).equipment
            self.pat_target = pile
            self.choose_text = 'choose_card_to_get'
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        else:
            self.pending_action = PendingAction.PLAY
            num = 2 if not self.character.check(self.game, chd.BillNoface) else self.max_lives-self.lives+1
            if self.character.check(self.game, chd.PixiePete): num += 1
            if self.character.check(self.game, tvosch.TucoFranziskaner) and not any((True for c in self.equipment if not c.usable_next_turn)): num += 2
            if (any((isinstance(c, grc.Piccone) for c in self.gold_rush_equipment))): num += 1
            if self.game.check_event(ceh.IlTreno) or (self.is_ghost and self.game.check_event(ceh.CittaFantasma)): num += 1
            elif self.game.check_event(ceh.Sete): num -= 1
            for i in range(num):
                if i == 0 and pile == 'scrap' and self.character.check(self.game, chars.PedroRamirez):
                    self.hand.append(self.game.deck.draw_from_scrap_pile())
                    G.sio.emit('chat_message', room=self.game.name, data=f'_draw_from_scrap|{self.name}')
                elif i == 0 and type(pile) == str and pile != self.name and pile in self.game.players_map and self.character.check(self.game, chars.JesseJones) and len(self.game.get_player_named(pile).hand) > 0:
                    self.hand.append(self.game.get_player_named(pile).hand.pop( randrange(0, len(self.game.get_player_named(pile).hand))))
                    self.game.get_player_named(pile).notify_self()
                    G.sio.emit('chat_message', room=self.game.name, data=f'_draw_from_player|{self.name}|{pile}')
                elif i == 1:
                    card: cs.Card = self.game.deck.draw()
                    if (self.character.check(self.game, chars.BlackJack) or self.game.check_event(ce.LeggeDelWest)):
                        for p in self.game.get_alive_players():
                            if p != self:
                                p.notify_card(self, card, 'blackjack_special' if self.character.check(self.game, chars.BlackJack) else 'foc.leggedelwest')
                        if self.game.check_event(ce.LeggeDelWest):
                            card.must_be_used = True
                        if self.character.check(self.game, chars.BlackJack) and card.check_suit(self.game, [cs.Suit.HEARTS, cs.Suit.DIAMONDS]):
                            self.game.deck.draw(player=self)
                    self.hand.append(card)
                    G.sio.emit('card_drawn', room=self.game.name, data={'player': self.name, 'pile': pile})
                else:
                    self.game.deck.draw(player=self)
            self.manette()
            self.notify_self()

    def manette(self):
        if self.game.check_event(ceh.Manette):
            self.choose_text = 'choose_manette'
            self.available_cards = [{
                'name': '',
                'icon': '♦♣♥♠'[s],
                'alt_text': '',
                'noDesc': True
            } for s in [0,1,2,3]]
            self.pending_action = PendingAction.CHOOSE

    def pick(self):
        if self.pending_action != PendingAction.PICK:
            return
        pickable_cards = 1 + self.character.pick_mod
        if any((isinstance(c, grc.FerroDiCavallo) for c in self.gold_rush_equipment)):
            pickable_cards += 1
        if self.is_my_turn and self.attacker is None:
            for i in range(len(self.equipment)):
                if i < len(self.equipment) and isinstance(self.equipment[i], cs.Dinamite):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cs.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        G.sio.emit('chat_message', room=self.game.name,
                                      data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                        if picked.check_suit(self.game, [cs.Suit.SPADES]) and 2 <= picked.number <= 9 and pickable_cards == 0:
                            self.lives -= 3
                            if any((isinstance(c, grc.Talismano) for c in self.gold_rush_equipment)):
                                self.gold_nuggets += 3
                            if self.character.check(self.game, grch.SimeonPicos):
                                self.gold_nuggets += 3
                            if any((isinstance(c, grc.Stivali) for c in self.gold_rush_equipment)):
                                self.game.deck.draw(player=self)
                                self.game.deck.draw(player=self)
                                self.game.deck.draw(player=self)
                            self.attacker = None
                            self.game.deck.scrap(self.equipment.pop(i), True, player=self)
                            G.sio.emit('chat_message', room=self.game.name, data=f'_explode|{self.name}')
                            self.heal_if_needed()
                            if self.character.check(self.game, chars.BartCassidy) and self.lives > 0:
                                for i in range(3):
                                    self.game.deck.draw(True, player=self)
                                G.sio.emit('chat_message', room=self.game.name, data=f'_special_bart_cassidy|{self.name}')
                            print(f'{self.name} Boom, -3 hp')
                            break
                        else:
                            self.game.next_player().equipment.append(self.equipment.pop(i))
                            self.game.next_player().notify_self()
                            break
                    if any((isinstance(c, cs.Dinamite) or isinstance(c, cs.Prigione) or isinstance(c, tvosc.SerpenteASonagli) for c in self.equipment)):
                        self.notify_self()
                        return
            for i in range(len(self.equipment)):
                if isinstance(self.equipment[i], cs.Prigione):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cs.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        G.sio.emit('chat_message', room=self.game.name,
                                      data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                        if not picked.check_suit(self.game, [cs.Suit.HEARTS]) and pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i), True, player=self)
                            G.sio.emit('chat_message', room=self.game.name, data=f'_prison_turn|{self.name}')
                            self.end_turn(forced=True)
                            return
                        elif pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i), True, player=self)
                            G.sio.emit('chat_message', room=self.game.name, data=f'_prison_free|{self.name}')
                            break
                    break
            for i in range(len(self.equipment)):
                if isinstance(self.equipment[i], tvosc.SerpenteASonagli):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cs.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        G.sio.emit('chat_message', room=self.game.name,
                                      data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                        if not picked.check_suit(self.game, [cs.Suit.SPADES]):
                            break
                        elif pickable_cards == 0:
                            self.lives -= 1
                            G.sio.emit('chat_message', room=self.game.name, data=f'_snake_bit|{self.name}')
                            if self.character.check(self.game, chars.BartCassidy):
                                G.sio.emit('chat_message', room=self.game.name, data=f'_special_bart_cassidy|{self.name}')
                                self.game.deck.draw(True, player=self)
                            if any((isinstance(c, grc.Talismano) for c in self.gold_rush_equipment)):
                                self.gold_nuggets += 1
                            if self.character.check(self.game, grch.SimeonPicos):
                                self.gold_nuggets += 1
                            if any((isinstance(c, grc.Stivali) for c in self.gold_rush_equipment)):
                                self.game.deck.draw(True, player=self)
                            break
            if any((isinstance(c, cs.Prigione) for c in self.equipment)):
                self.notify_self() #TODO perchè solo le prigioni? e multiple dinamiti come si comportano con veracuster?
                return
            if isinstance(self.real_character, chd.VeraCuster):
                self.set_available_character([p.character for p in self.game.get_alive_players() if p != self])
            else:
                self.pending_action = PendingAction.DRAW
            self.notify_self()
        else:
            self.pending_action = PendingAction.WAIT
            self.on_pick_cb()

    def get_playable_cards(self):
        playable_cards = []
        for i in range(len(self.hand)):
            card = self.hand[i]
            if isinstance(card, cs.Bang) and self.has_played_bang and not any((isinstance(c, cs.Volcanic) for c in self.equipment)):
                continue
            elif isinstance(card, cs.Birra) and self.lives >= self.max_lives:
                continue
            else:
                playable_cards.append(i)
        return playable_cards

    def play_card(self, hand_index: int, against=None, _with=None):
        if self.is_bot:
            data = {
                "index": hand_index,
                "against": against,
                "with": _with
            }
            self.game.rpc_log.append(f'{self.name};play_card;{json.dumps(data)}')
        print(self.name, 'wants to play card ', hand_index, ' against:', against, ' with:', _with)
        if not self.is_my_turn or self.pending_action != PendingAction.PLAY or self.game.is_handling_death:
            print('but cannot')
            return
        if not (0 <= hand_index < len(self.hand) + len(self.equipment) + len(self.gold_rush_equipment)):
            print('but the card index is out of range')
            return
        elif len(self.hand) + len(self.equipment) <= hand_index < len(self.hand) + len(self.equipment) + len(self.gold_rush_equipment) and len(self.gold_rush_equipment):
            print('which is a gold rush black card')
            card: grc.ShopCard = self.gold_rush_equipment[hand_index - len(self.hand) - len(self.equipment)]
            return card.play_card(self)
        from_hand = hand_index < len(self.hand)
        card: cs.Card = self.hand.pop(hand_index) if hand_index < len(self.hand) else self.equipment.pop(hand_index-len(self.hand))
        withCard: cs.Card = None
        if _with is not None:
            withCard = self.hand.pop(_with) if hand_index > _with else self.hand.pop(_with - 1)
        print(self.name, 'is playing ', card, ' against:', against, ' with:', _with)
        did_play_card = False
        event_blocks_card = (self.game.check_event(ce.IlGiudice) and (card.is_equipment or (card.usable_next_turn and not card.can_be_used_now))) or (self.game.check_event(ce.Lazo) and card.usable_next_turn and card.can_be_used_now) or ((self.game.check_event(ceh.Manette) and card.suit != self.committed_suit_manette))
        if not(against is not None and (self.game.get_player_named(against).character.check(self.game, chd.ApacheKid) or any((isinstance(c, grc.Calumet) for c in self.game.get_player_named(against).gold_rush_equipment))) and card.check_suit(self.game, [cs.Suit.DIAMONDS])) or (isinstance(card, grc.ShopCard) and card.kind == grc.ShopCardKind.BLACK) and not event_blocks_card:
            if (against == self.name and not isinstance(card, csd.Tequila) and not isinstance(card, cs.Panico) and not isinstance(card, cs.CatBalou)) or event_blocks_card:
                did_play_card = False
            else:
                did_play_card = card.play_card(self, against, withCard)
        if not card.is_equipment and not card.usable_next_turn and not (isinstance(card, grc.ShopCard) and card.kind == grc.ShopCardKind.BLACK) or (event_blocks_card and not (card.usable_next_turn and card.can_be_used_now)):
            if did_play_card:
                self.game.deck.scrap(card, True)
            else:
                self.hand.insert(hand_index, card)
                if withCard:
                    self.hand.insert(_with, withCard)
                G.sio.emit('cant_play_card', room=self.sid)
        elif (card.usable_next_turn and card.can_be_used_now) or (isinstance(card, grc.ShopCard) and card.kind == grc.ShopCardKind.BLACK) or event_blocks_card:
            if did_play_card:
                self.game.deck.scrap(card, True)
            else:
                self.equipment.insert(hand_index-len(self.hand), card)
        elif card.is_equipment or (card.usable_next_turn and not card.can_be_used_now):
            if not did_play_card:
                if from_hand:
                    self.hand.insert(hand_index, card)
                else:
                    self.equipment.insert(hand_index-len(self.hand), card)
            else:
                did_play_card = True
        if not self.game.is_replay:
            Metrics.send_metric('play_card', points=[1], tags=[f'success:{did_play_card}', f'card:{card.name}', f'bot:{self.is_bot}', f'exp:{card.expansion if "expansion" in card.__dict__ else "vanilla"}'])
        print("did play card:", did_play_card)
        self.notify_self()
        if self.is_bot:
            return did_play_card or card.is_equipment or (card.usable_next_turn and not card.can_be_used_now)

    def choose(self, card_index):
        if self.pending_action != PendingAction.CHOOSE:
            return
        if self.target_p and self.target_p != '':  # panico, cat balou, rissa
            target = self.game.get_player_named(self.target_p)
            card = None
            if (target.name == self.name):
                card = self.equipment.pop(card_index if card_index < len(target.hand) else card_index - len(target.hand))
            elif card_index >= len(target.hand):
                card = target.equipment.pop(card_index - len(target.hand))
            else:
                card = target.hand.pop(card_index)
            target.notify_self()
            if self.choose_action == 'steal':
                G.sio.emit('card_drawn', room=self.game.name, data={'player': self.name, 'pile': target.name})
                card.reset_card()
                if card.name != "Fantasma" or self.name != target.name: #se si uccide facendo panico su fantasma la carta non gli viene messa in mano
                    self.hand.append(card)
            else:
                self.game.deck.scrap(card, True, player=target)
            if self.event_type != 'rissa' or len(self.rissa_targets) == 0:
                self.event_type = ''
                self.target_p = ''
                self.choose_action = ''
                self.pending_action = PendingAction.PLAY
            else:
                self.target_p = self.rissa_targets.pop(0).name
                print(f'rissa targets: {self.rissa_targets}')
            self.notify_self()
        elif self.choose_text == 'choose_ricercato':
            player = self.game.get_player_named(self.available_cards[card_index]['name'])
            G.sio.emit('chat_message', room=player.game.name, data=f'_play_card_against|{self.name}|Ricercato|{player.name}')
            if any((isinstance(c, grc.Ricercato) for c in player.gold_rush_equipment)):
                self.game.deck.shop_deck.append(grc.Ricercato())
            else:
                player.gold_rush_equipment.append(grc.Ricercato())
            player.notify_self()
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_sid_scrap':
            self.scrapped_cards += 1
            self.game.deck.scrap(self.hand.pop(card_index), True, player=self)
            if self.scrapped_cards == 2:
                self.available_cards = []
                self.pending_action = self.previous_pending_action
                if self.game.players[self.game.turn] != self:
                    self.game.players[self.game.turn].pending_action = PendingAction.PLAY
                    self.game.players[self.game.turn].notify_self()
            self.notify_self()
        elif self.choose_text == 'choose_bicchierino':
            player = self.game.get_player_named(self.available_cards[card_index]['name'])
            G.sio.emit('chat_message', room=self.game.name, data=f'_play_card_for|{self.name}|{"Bicchierino"}|{player.name}')
            player.lives = min(player.lives+1, player.max_lives)
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_birra_function':
            if card_index == 0:
                self.gold_nuggets += 1
                G.sio.emit('chat_message', room=self.game.name, data=f'_get_nugget|{self.name}')
            else:
                cs.Birra(1,1).play_card(self, skipChecks=True)
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_bottiglia':
            G.sio.emit('chat_message', room=self.game.name, data=f'_play_card|{self.name}|{"Bottiglia"}')
            if isinstance(self.available_cards[card_index], cs.Birra):
                self.lives = min(self.lives+1, self.max_lives)
            else:
                self.hand.append(self.available_cards[card_index])
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_complice':
            G.sio.emit('chat_message', room=self.game.name, data=f'_play_card|{self.name}|{"Bottiglia"}')
            self.hand.append(self.available_cards[card_index])
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'gold_rush_discard':
            if card_index == len(self.available_cards) - 1:
                self.pending_action = PendingAction.PLAY
            else:
                player = self.game.get_player_named(self.available_cards[card_index]['name'])
                self.available_cards = [c for c in player.gold_rush_equipment if c.number+1 <= self.gold_nuggets]
                self.available_cards.append({'icon': '❌', 'noDesc': True})
                self.choose_text = 'gold_rush_discard_2|' + player.name
            self.notify_self()
        elif 'gold_rush_discard_2' in self.choose_text:
            if card_index == len(self.available_cards) - 1:
                self.pending_action = PendingAction.PLAY
            else:
                self.gold_nuggets -= self.available_cards[card_index].number + 1
                player = self.game.get_player_named(self.choose_text.split('|')[1])
                player.gold_rush_equipment.remove(self.available_cards[card_index])
                self.game.deck.shop_deck.append(self.available_cards[card_index])
                G.sio.emit('chat_message', room=self.game.name, data=f'_gold_rush_pay_discard|{self.name}|{player.name}|{self.available_cards[card_index].name}')
                player.notify_self()
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif 'choose_fantasma' in self.choose_text:
            if card_index <= len(self.available_cards):
                player = self.game.get_player_named(self.available_cards[card_index]['name'])
                player.equipment.append(self.game.deck.scrap_pile.pop(-1))
                player.notify_self()
                self.game.notify_all()
                G.sio.emit('chat_message', room=player.game.name, data=f'_play_card_against|{self.name}|Fantasma|{player.name}')
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif 'choose_sventagliata' in self.choose_text:
            if card_index <= len(self.available_cards):
                og = self.available_cards[card_index]['original_target']
                player = self.game.get_player_named(self.available_cards[card_index]['name'])
                player.game.attack(self, og, card_name='Sventagliata')
                player.game.attack(self, player.name, card_name='Sventagliata')
                G.sio.emit('chat_message', room=player.game.name, data=f'_play_card_against|{self.name}|Sventagliata|{og}')
                G.sio.emit('chat_message', room=player.game.name, data=f'_play_card_against|{self.name}|Sventagliata|{player.name}')
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif 'choose_play_as_bang' in self.choose_text:
            if card_index <= len(self.available_cards):
                self.hand.remove(self.available_cards[card_index])
                self.game.deck.scrap(self.available_cards[card_index], player=self)
                self.hand.append(cs.Bang(self.available_cards[card_index].suit, 42))
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif 'choose_tornado' in self.choose_text:
            if card_index <= len(self.available_cards):
                self.game.deck.scrap(self.hand.pop(card_index), player=self)
                self.game.deck.draw(player=self)
                self.game.deck.draw(player=self)
            self.pending_action = PendingAction.WAIT
            self.game.responders_did_respond_resume_turn()
            self.notify_self()
        elif 'choose_poker' in self.choose_text:
            if card_index <= len(self.available_cards):
                self.game.deck.scrap(self.hand.pop(card_index), player=self)
            self.pending_action = PendingAction.WAIT
            self.game.responders_did_respond_resume_turn()
            self.notify_self()
        elif 'choose_from_poker' in self.choose_text:
            st_idx = len(self.game.deck.scrap_pile)-len(self.available_cards)
            self.available_cards.pop(card_index)
            self.hand.append(self.game.deck.scrap_pile.pop(st_idx + card_index))
            self.game.notify_scrap_pile()
            if self.choose_text.split(';')[1] == '1':
                self.pending_action = PendingAction.PLAY
            else: self.choose_text = 'choose_from_poker;1'
            self.notify_self()
        elif 'choose_bandidos' in self.choose_text:
            if card_index < len(self.hand):
                self.available_cards.pop(card_index)
                self.game.deck.scrap(self.hand.pop(card_index), player=self)
                self.mancato_needed -= 1
            else:
                self.lives -= 1
                self.mancato_needed = 0
            if self.mancato_needed <= 0:
                self.pending_action = PendingAction.WAIT
                self.game.responders_did_respond_resume_turn()
            self.notify_self()
        elif self.game.check_event(ceh.NuovaIdentita) and self.choose_text == 'choose_nuova_identita':
            if card_index == 1: # the other character
                self.character = self.not_chosen_character
                self.real_character = self.character
                self.max_lives = self.character.max_lives + self.role.health_mod
                self.lives = 2
                G.sio.emit('chat_message', room=self.game.name, data=f'_choose_character|{self.name}|{self.character.name}')
            self.play_turn(again = True)
        elif self.game.check_event(ceh.Manette) and self.choose_text == 'choose_manette':
            self.committed_suit_manette = cs.Suit(card_index)
            G.sio.emit('chat_message', room=self.game.name, data=f'_choose_manette|{self.name}|{"♦♣♥♠"[card_index]}')
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.is_giving_life and self.game.check_event(ce.FratelliDiSangue):
            try:
                player = self.game.get_player_named(self.available_cards[card_index]['name'])
                player.lives += 1
                self.lives -= 1
                player.notify_self()
                G.sio.emit('chat_message', room=self.game.name, data=f'_fratelli_sangue|{self.name}|{player.name}')
            except: pass
            self.play_turn(again = True)
        elif self.is_using_checchino and self.game.check_event(ce.Cecchino):
            try:
                if self.available_cards[card_index]['name'] != '':
                    for _ in range(2):
                        card = next(c for c in self.hand if c.name == cs.Bang(0,0).name)
                        self.hand.remove(card)
                        self.game.deck.scrap(card, True)
                    self.pending_action = PendingAction.PLAY
                    self.game.attack(self, self.available_cards[card_index]['name'], double=True)
            except:
                self.pending_action = PendingAction.PLAY
            self.is_using_checchino = False
            self.notify_self()
        elif self.using_rimbalzo > 0 and self.game.check_event(ce.Rimbalzo):
            if self.using_rimbalzo == 1 and 'name' in self.available_cards[card_index]:
                self.rimbalzo_p = self.available_cards[card_index]['name']
                self.available_cards = self.game.get_player_named(self.available_cards[card_index]['name']).equipment
                self.choose_text = 'choose_rimbalzo_card'
                self.using_rimbalzo = 2
            elif self.using_rimbalzo == 2 and 'name' in self.available_cards[card_index].__dict__:
                card = next(c for c in self.hand if c.name == cs.Bang(0,0).name)
                self.hand.remove(card)
                self.game.deck.scrap(card, True)
                self.using_rimbalzo = 0
                self.available_cards = []
                self.pending_action = PendingAction.PLAY
                self.game.rimbalzo(self, self.rimbalzo_p, card_index)
            else:
                self.using_rimbalzo = 0
                self.rimbalzo_p = ''
                self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.is_playing_ranch and self.game.check_event(ce.Ranch):
            if card_index == len(self.available_cards) - 1:
                self.hand = [c for c in self.hand if c not in self.discarded_cards]
                for i in range(len(self.discarded_cards)):
                    self.game.deck.scrap(self.discarded_cards[i], True, player=self)
                    self.game.deck.draw(player=self)
                self.discarded_cards = []
                self.is_playing_ranch = False
                self.pending_action = PendingAction.PLAY
            else:
                self.discarded_cards.append(self.available_cards.pop(card_index))
            self.notify_self()
        elif self.game.dalton_on and self.game.check_event(ceh.IDalton):
            card = next(c for c in self.equipment if c == self.available_cards[card_index])
            self.equipment.remove(card)
            self.game.deck.scrap(card, True, player=self)
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.responders_did_respond_resume_turn()
        elif self.is_drawing and self.game.check_event(ce.Peyote):
            self.is_drawing = False
            card = self.game.deck.draw()
            G.sio.emit('chat_message', room=self.game.name, data=f"_guess|{self.name}|{self.available_cards[card_index]['icon']}")
            self.available_cards = []
            if card_index == card.suit%2:
                self.hand.append(card)
                G.sio.emit('chat_message', room=self.game.name, data=f"_guess_right|{self.name}")
                self.pending_action = PendingAction.DRAW
            else:
                self.game.deck.scrap(card)
                G.sio.emit('chat_message', room=self.game.name, data=f"_guess_wrong|{self.name}")
                self.pending_action = PendingAction.PLAY
            self.notify_self()
        # specifico per personaggio
        elif self.is_drawing and self.character.check(self.game, chars.KitCarlson):
            card: cs.Card = self.available_cards.pop(card_index)
            if len(self.available_cards) == 1: #ho pescato la seconda carta
                if self.game.check_event(ce.LeggeDelWest):
                    card.must_be_used = True
            self.hand.append(card)
            pickable_stop = 1
            if self.game.check_event(ceh.Sete): pickable_stop += 1
            if self.game.check_event(ceh.IlTreno) or any((isinstance(c, grc.Piccone) for c in self.gold_rush_equipment)):
                pickable_stop -= 1
            if len(self.available_cards) == pickable_stop:
                if len(self.available_cards) > 0: #la carta non scelta la rimettiamo in cima al mazzo
                    self.game.deck.put_on_top(self.available_cards.pop())
                if len(self.available_cards) > 0: #se sono rimaste carte le scartiamo
                    self.game.deck.scrap(self.available_cards.pop())
                #se c'è sia treno che piccone pesco un'altra carta
                if self.game.check_event(ceh.IlTreno) and any((isinstance(c, grc.Piccone) for c in self.gold_rush_equipment)):
                    self.game.deck.draw(player=self)
                self.is_drawing = False
                self.pending_action = PendingAction.PLAY
                self.manette()
            self.notify_self()
        # specifico per personaggio
        elif self.is_drawing and self.character.check(self.game, grch.DutchWill):
            if not self.game.check_event(ceh.Sete):
                self.hand.append(self.available_cards.pop(card_index)) #prendo la carta scelta
            else:
                self.game.deck.scrap(self.available_cards.pop(0), True) #non pesco carte
            self.game.deck.scrap(self.available_cards.pop(0), True) #scarto l'altra
            #legge del west non si applica perchè la seconda carta viene scartata
            if self.game.check_event(ceh.IlTreno):
                self.game.deck.draw(player=self)
            if any((isinstance(c, grc.Piccone) for c in self.gold_rush_equipment)):
                self.game.deck.draw(player=self)
            self.gold_nuggets += 1
            self.is_drawing = False
            self.pending_action = PendingAction.PLAY
            self.manette()
            self.notify_self()
        # specifico per personaggio
        elif self.is_drawing and self.character.check(self.game, chd.PatBrennan):
            #non pesca per niente dal mazzo 
            self.is_drawing = False
            card = self.available_cards.pop(card_index)
            card.reset_card()
            self.hand.append(card)
            self.available_cards = []
            G.sio.emit('card_drawn', room=self.game.name, data={'player': self.name, 'pile': self.pat_target})
            self.game.get_player_named(self.pat_target).notify_self()
            self.pending_action = PendingAction.PLAY
            self.manette()
            self.notify_self()
        else:  # emporio
            self.game.respond_emporio(self, card_index)

    def barrel_pick(self):
        pickable_cards = 1 + self.character.pick_mod
        if any((isinstance(c, grc.FerroDiCavallo) for c in self.gold_rush_equipment)):
            pickable_cards += 1
        if any((isinstance(c, cs.Barile) for c in self.equipment)) and self.character.check(self.game, chars.Jourdonnais):
            pickable_cards = 2
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cs.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            G.sio.emit('chat_message', room=self.game.name,
                            data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
            if picked.check_suit(self.game, [cs.Suit.HEARTS]):
                self.mancato_needed -= 1
                self.notify_self()
                if self.mancato_needed <= 0:
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                    return
        if not self.game.is_competitive and not any((isinstance(c, cs.Mancato) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente) for c in self.hand))\
             and not any((c.can_be_used_now and isinstance(c, cs.Mancato) for c in self.equipment)):
            self.take_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = self.game.deck.mancato_cards.copy()
            if self.character.check(self.game, chars.CalamityJanet) and cs.Bang(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Bang(0, 0).name)
            self.on_failed_response_cb = self.take_damage_response
            self.notify_self()

    def barrel_pick_no_dmg(self):
        pickable_cards = 1 + self.character.pick_mod
        if any((isinstance(c, cs.Barile) for c in self.equipment)) and self.character.check(self.game, chars.Jourdonnais):
            pickable_cards = 2
        if any((isinstance(c, grc.FerroDiCavallo) for c in self.gold_rush_equipment)):
            pickable_cards += 1
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cs.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            G.sio.emit('chat_message', room=self.game.name,
                            data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
            if picked.check_suit(self.game, [cs.Suit.HEARTS]):
                self.mancato_needed -= 1
                self.notify_self()
                if self.mancato_needed <= 0:
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                    return
        if not self.game.is_competitive and not any((isinstance(c, cs.Mancato) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente) for c in self.hand))\
             and not any((c.can_be_used_now and isinstance(c, cs.Mancato) for c in self.equipment)):
            self.take_no_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = self.game.deck.mancato_cards.copy()
            if self.character.check(self.game, chars.CalamityJanet) and cs.Bang(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Bang(0, 0).name)
            self.on_failed_response_cb = self.take_no_damage_response
            self.notify_self()

    def get_discarded(self, attacker=None, card_name=None, action=None):
        if card_name in {'Tornado', 'Poker', 'Bandidos'}:
            self.pending_action = PendingAction.CHOOSE
            self.available_cards = self.hand.copy()
            if card_name == 'Tornado':
                self.choose_text = 'choose_tornado'
            if card_name == 'Poker':
                self.choose_text = 'choose_poker'
            if card_name == 'Bandidos':
                self.choose_text = 'choose_bandidos'
                self.mancato_needed = min(2, len(self.hand))
                self.available_cards.append({'name': '-1hp', 'icon': '💔', 'noDesc': True})
            return True
        else:
            if self.can_escape(card_name) or self.character.check(self.game, tvosch.MickDefender):
                self.pending_action = PendingAction.RESPOND
                self.mancato_needed = 1
                self.attacker = attacker
                self.attacking_card = card_name
                self.expected_response = ['Fuga']
                if self.can_escape(with_mancato=True):
                    self.expected_response.append(cs.Mancato(0, 0).name)
                if action == 'steal':
                    self.on_failed_response_cb = self.take_steal_response
                else:
                    self.on_failed_response_cb = self.take_discard_response
                self.notify_self()
                return True

    def take_steal_response(self):
        self.attacker.pending_action = PendingAction.CHOOSE
        self.attacker.target_p = self.name
        self.attacker.choose_text = 'steal'
        self.take_no_damage_response()

    def take_discard_response(self):
        self.attacker.pending_action = PendingAction.CHOOSE
        self.attacker.target_p = self.name
        self.attacker.choose_text = 'discard'
        self.take_no_damage_response()
    
    def can_escape(self, card_name:str=None, with_mancato:bool=False):
        if card_name == 'Bang!' or card_name in self.game.deck.green_cards:
            return False
        if any((isinstance(c, tvosc.Fuga) for c in self.hand)) and not with_mancato:
            return True
        return with_mancato and self.character.check(self.game, tvosch.MickDefender)

    def get_banged(self, attacker, double:bool=False, no_dmg:bool=False, card_index:int|None=None, card_name:str|None=None):
        self.attacker = attacker
        self.attacking_card = card_name
        print(f'attacker -> {attacker}')
        if isinstance(attacker, Player) and attacker.character.check(self.game, tvosch.ColoradoBill) and card_name == 'Bang!':
            picked: cs.Card = self.game.deck.pick_and_scrap()
            G.sio.emit('chat_message', room=self.game.name, data=f'_flipped|{attacker.name}|{picked.name}|{picked.num_suit()}')
            if picked.check_suit(self.game, [cs.Suit.SPADES]):
                self.take_damage_response()
                return False
        self.mancato_needed = 1 if not double else 2
        if card_index is not None:
            self.dmg_card_index = card_index
        else:
            self.dmg_card_index = -1
        for i in range(len(self.equipment)):
            if self.equipment[i].can_be_used_now:
                print('usable', self.equipment[i])
        if (not self.game.is_competitive and not any((isinstance(c, cs.Barile) for c in self.equipment)) and not self.character.check(self.game, chars.Jourdonnais)\
             and not any(((isinstance(c, cs.Mancato) and c.can_be_used_now) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente) for c in self.hand))\
             and not any((c.can_be_used_now and isinstance(c, cs.Mancato) for c in self.equipment)) and not self.can_escape(card_name)) or card_name=='Mira':
            print('Cant defend')
            if not no_dmg:
                self.take_damage_response()
            else:
                self.take_no_damage_response()
            return False
        else:
            if ((not self.game.check_event(ce.Lazo) and any((isinstance(c, cs.Barile) for c in self.equipment))) \
                 and not (self.game.players[self.game.turn].character.check(self.game, chd.BelleStar) and isinstance(attacker, Player))) \
                 or self.character.check(self.game, chars.Jourdonnais): #se ho un barile e non c'è lazo e non mi sta attaccando Belle Star o se sono Jourdonnais
                print('has barrel')
                self.pending_action = PendingAction.PICK
                if not no_dmg:
                    self.on_pick_cb = self.barrel_pick
                else:
                    self.on_pick_cb = self.barrel_pick_no_dmg
            else:
                print('has mancato')
                self.pending_action = PendingAction.RESPOND
                self.expected_response = self.game.deck.mancato_cards.copy()
                if self.attacker and self.attacker in self.game.get_alive_players() and attacker.character.check(self.game, chd.BelleStar) or self.game.check_event(ce.Lazo):
                    self.expected_response = self.game.deck.mancato_cards_not_green_or_blue.copy()
                if self.character.check(self.game, chars.CalamityJanet) and cs.Bang(0, 0).name not in self.expected_response:
                    self.expected_response.append(cs.Bang(0, 0).name)
                if self.can_escape(card_name, with_mancato=False):
                    self.expected_response.append(tvosc.Fuga(0, 0).name)
                if not no_dmg:
                    self.on_failed_response_cb = self.take_damage_response
                else:
                    self.on_failed_response_cb = self.take_no_damage_response
            return True

    def get_dalton(self):
        equipments = [c for c in self.equipment if not c.usable_next_turn]
        if len(equipments) == 0:
            return False
        else:
            self.choose_text = 'choose_dalton'
            self.pending_action = PendingAction.CHOOSE
            self.available_cards = equipments
            return True

    def get_indians(self, attacker):
        self.attacker = attacker
        self.attacking_card = "Indiani!"
        if self.character.check(self.game, chd.ApacheKid) or any((isinstance(c, grc.Calumet) for c in self.gold_rush_equipment)): return False
        if not self.game.is_competitive and not any((isinstance(c, cs.Bang) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Mancato)) for c in self.hand)) and not self.can_escape():
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            print('has bang')
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cs.Bang(0, 0).name, tvosc.Fuga(0, 0).name]
            if (self.character.check(self.game, chars.CalamityJanet) or self.can_escape(with_mancato=True)) and cs.Mancato(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Mancato(0, 0).name)
            self.event_type = 'indians'
            self.on_failed_response_cb = self.take_damage_response
            return True

    def get_dueled(self, attacker):
        self.attacker = attacker
        self.attacking_card = "Duello"
        if (self.game.check_event(ceh.Sermone) and self.is_my_turn) or (not self.game.is_competitive and not any((isinstance(c, cs.Bang) or isinstance(c, tvosc.Fuga) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Mancato)) for c in self.hand))):
            print('Cant defend')
            self.take_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
            return False
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cs.Bang(0, 0).name, tvosc.Fuga(0, 0).name]
            if (self.character.check(self.game, chars.CalamityJanet) or self.can_escape(with_mancato=True)) and cs.Mancato(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Mancato(0, 0).name)
            self.event_type = 'duel'
            self.on_failed_response_cb = self.take_damage_response
            return True

    def heal_if_needed(self):
        while self.lives <= 0 and len(self.game.get_alive_players()) > 2 and any((isinstance(c, cs.Birra) for c in self.hand)) and not self.game.check_event(ceh.IlReverendo):
            for i in range(len(self.hand)):
                if isinstance(self.hand[i], cs.Birra):
                    if self.character.check(self.game, chd.MollyStark) and not self.is_my_turn:
                        self.game.deck.draw(True, player=self)
                    self.lives += 1 if not self.character.check(self.game, chd.TequilaJoe) else 2
                    self.lives = min(self.lives, self.max_lives)
                    self.game.deck.scrap(self.hand.pop(i), True, player=self)
                    G.sio.emit('chat_message', room=self.game.name,
                                  data=f'_beer_save|{self.name}')
                    break

    def take_damage_response(self):
        self.lives -= 1
        G.sio.emit('hurt', room=self.sid, data=f'')
        if self.lives > 0:
            if self.character.check(self.game, chars.BartCassidy):
                G.sio.emit('chat_message', room=self.game.name,
                                data=f'_special_bart_cassidy|{self.name}')
                self.game.deck.draw(True, player=self)
            elif self.character.check(self.game, chars.ElGringo) and self.attacker and self.attacker in self.game.get_alive_players() and len(self.attacker.hand) > 0:
                self.hand.append(self.attacker.hand.pop(randrange(0, len(self.attacker.hand))))
                self.hand[-1].reset_card()
                G.sio.emit('card_drawn', room=self.game.name, data={'player': self.name, 'pile': self.attacker.name})
                G.sio.emit('chat_message', room=self.game.name,
                              data=f'_special_el_gringo|{self.name}|{self.attacker.name}')
                self.attacker.notify_self()
        if isinstance(self.attacker, Player) and not self.game.check_event(ce.Lazo):
            if any((isinstance(c, tvosc.Taglia) for c in self.equipment)):
                self.game.deck.draw(True, player=self.attacker)
                G.sio.emit('chat_message', room=self.game.name,
                    data=f'_taglia_reward|{self.name}|{self.attacker.name}')
                self.attacker.notify_self()
            if len(self.hand) > 0 and any((isinstance(cd, tvosc.Shotgun) for cd in self.attacker.equipment)):
                c = self.hand.pop(randrange(0, len(self.hand)))
                self.game.deck.scrap(c, True, player=self)
                G.sio.emit('chat_message', room=self.game.name, data=f'_shotgun_scrap|{self.name}|{c.name}')
        if self.attacker and 'gold_rush' in self.game.expansions and not self.is_ghost:
            if (isinstance(self.attacker, Player)):
                self.attacker.gold_nuggets += 1
                self.attacker.notify_self()
            if any((isinstance(c, grc.Talismano) for c in self.gold_rush_equipment)):
                self.gold_nuggets += 1
            if self.character.check(self.game, grch.SimeonPicos):
                self.gold_nuggets += 1
            if any((isinstance(c, grc.Stivali) for c in self.gold_rush_equipment)):
                self.game.deck.draw(True, player=self)
        self.heal_if_needed()
        self.mancato_needed = 0
        self.expected_response = []
        self.attacking_card = None
        self.event_type = ''
        self.notify_self()
        self.attacker = None

    def take_no_damage_response(self):
        if self.dmg_card_index is not None and self.dmg_card_index != -1 and self.game.check_event(ce.Rimbalzo):
            self.game.deck.scrap(self.equipment.pop(self.dmg_card_index), player=self)
        self.dmg_card_index = -1
        self.mancato_needed = 0
        self.expected_response = []
        self.attacking_card = None
        self.event_type = ''
        self.notify_self()
        self.attacker = None

    def respond(self, hand_index):
        if self.pending_action != PendingAction.RESPOND: return
        self.pending_action = PendingAction.WAIT
        if hand_index != -1 and hand_index < (len(self.hand)+len(self.equipment)) and (
            ((hand_index < len(self.hand) and self.hand[hand_index].name in self.expected_response) or self.character.check(self.game, chd.ElenaFuente)) or
            (0 <= hand_index-len(self.hand) < len(self.equipment) and self.equipment[hand_index-len(self.hand)].name in self.expected_response)):
            card = self.hand.pop(hand_index) if hand_index < len(self.hand) else self.equipment.pop(hand_index-len(self.hand))
            #hand_index < len(self.hand) with the '<=' due to the hand.pop
            if self.character.check(self.game, chd.MollyStark) and 0 <= hand_index <= len(self.hand) and not self.is_my_turn and self.event_type != 'duel':
                if hasattr(self.attacker,'character') and self.attacker.character.check(self.game, chars.SlabTheKiller) and isinstance(card, cs.Mancato):
                    self.molly_discarded_cards += 1
                else:
                    self.game.deck.draw(True, player=self)
            card.use_card(self)
            print(f'{self.game.name}: {self.name} responded with {card.name}')
            G.sio.emit('chat_message', room=self.game.name, data=f'_respond|{self.name}|{card.name}')
            self.game.deck.scrap(card, True, player=self)
            self.notify_self()
            self.mancato_needed -= 1
            if isinstance(card, tvosc.RitornoDiFiamma):
                self.game.attack(self, self.attacker.name, card_name=card.name)
            if self.mancato_needed <= 0:
                if self.event_type == 'duel':
                    if isinstance(card, tvosc.Fuga) or (isinstance(card, cs.Mancato) and self.character.check(self.game, tvosch.MickDefender)):
                        self.game.responders_did_respond_resume_turn(did_lose=False)
                    else:
                        self.game.duel(self, self.attacker.name)
                        if self.character.check(self.game, chd.MollyStark) and hand_index < len(self.hand) and not self.is_my_turn:
                            self.molly_discarded_cards += 1
                else:
                    if self.character.check(self.game, chd.MollyStark) and not self.is_my_turn:
                        for i in range(self.molly_discarded_cards):
                            self.game.deck.draw(True, player=self)
                        self.molly_discarded_cards = 0
                        self.notify_self()
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                self.event_type = ''
            elif not any(((isinstance(c, cs.Mancato) and c.can_be_used_now) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente) for c in self.hand)) and not any((c.can_be_used_now and isinstance(c, cs.Mancato) for c in self.equipment)):
                self.on_failed_response_cb()
                if self.game:
                    self.game.responders_did_respond_resume_turn(did_lose=True)
            else:
                self.pending_action = PendingAction.RESPOND
                self.notify_self()
        else:
            if self.character.check(self.game, chd.MollyStark) and not self.is_my_turn:
                for i in range(self.molly_discarded_cards):
                    self.game.deck.draw(True, player=self)
                self.molly_discarded_cards = 0
                self.notify_self()
            elif self.attacker and self.attacker in self.game.get_alive_players() and self.attacker.character.check(self.game, chd.MollyStark) and self.is_my_turn:
                for i in range(self.attacker.molly_discarded_cards):
                    self.attacker.game.deck.draw(True, player=self.attacker)
                self.attacker.molly_discarded_cards = 0
                self.attacker.notify_self()
            self.on_failed_response_cb()
            if self.game:
                self.game.responders_did_respond_resume_turn(did_lose=True)
        if self.mancato_needed <= 0:
            self.attacker = None

    def get_sight(self, countWeapon=True): #come vedo io gli altri
        if not self.character:
            return 0
        if self.game.check_event(ce.Lazo):
            return 1 + self.character.sight_mod
        aim = 0
        range = 0
        for card in self.equipment:
            if card.is_weapon and countWeapon:
                range += card.range
            else:
                aim += card.sight_mod
        return max(1,range) + aim + (self.character.sight_mod if not self.game.check_event(ceh.Sbornia) else 0)

    def get_visibility(self): #come mi vedono gli altri
        if not self.character or not self.game or not self.game.players[self.game.turn].character:
            return 0
        covers = 0
        ch_vis_mod = self.character.visibility_mod if not self.game.check_event(ceh.Sbornia) else 0
        if self.game.check_event(ce.Lazo) or self.game.players[self.game.turn].character.check(self.game, chd.BelleStar):
            return ch_vis_mod
        for card in self.equipment:
            covers += card.vis_mod
        return ch_vis_mod + covers

    def scrap(self, card_index):
        if len(self.hand) == 0 or len(self.hand) <= card_index: return self.notify_self()
        if self.is_my_turn or self.character.check(self.game, chars.SidKetchum):
            self.scrapped_cards += 1
            card = self.hand.pop(card_index)
            if self.character.check(self.game, chars.SidKetchum) and self.scrapped_cards == 2:
                self.scrapped_cards = 0
                self.lives = min(self.lives+1, self.max_lives)
            elif self.character.check(self.game, chd.JoseDelgado) and card.is_equipment and self.special_use_count < 2:
                self.game.deck.draw(True, player=self)
                self.game.deck.draw(True, player=self)
                self.special_use_count += 1
            self.game.deck.scrap(card, player=self)
            self.notify_self()

    def special(self, data):
        self.character.special(self, data)

    def gold_rush_discard(self):
        self.available_cards = [{
            'name': p.name,
            'icon': p.role.icon if(self.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
            'is_character': True,
            'avatar': p.avatar,
            'alt_text': ''.join(['🎴️'] * len(p.gold_rush_equipment)),
            'is_player': True
        } for p in self.game.get_alive_players() if p != self and any((e.number + 1 <= self.gold_nuggets for e in p.gold_rush_equipment))]
        self.available_cards.append({'icon': '❌', 'noDesc': True})
        self.choose_text = 'gold_rush_discard'
        self.pending_action = PendingAction.CHOOSE
        self.notify_self()

    def buy_gold_rush_card(self, index):
        print(f'{self.name} wants to buy gr-card index {index} in room {self.game.name}')
        card: cs.Card = self.game.deck.shop_cards[index]
        discount = 0
        if self.character.check(self.game, grch.PrettyLuzena) and self.special_use_count < 1:
            discount = 1
        if self.pending_action == PendingAction.PLAY and self.gold_nuggets >= card.number - discount:
            self.gold_nuggets -= card.number - discount
            if self.character.check(self.game, grch.PrettyLuzena) and self.special_use_count < 1:
                self.special_use_count += 1
            if card.play_card(self):
                self.game.deck.shop_deck.append(card)
            self.game.deck.shop_cards[index] = None
            self.game.deck.fill_gold_rush_shop()
            self.notify_self()

    def check_can_end_turn(self):
        must_be_used_cards = [c for c in self.hand if c.must_be_used]
        if self.game.check_event(ce.LeggeDelWest) and len(must_be_used_cards) > 0:
            card = must_be_used_cards[0]
            print(f'Legge del west card: {card.name}')
            print(self.has_played_bang and not (any((isinstance(c, cs.Volcanic) for c in self.equipment)) and type(card) == type(cs.Bang)))
            if card.suit == cs.Suit.DIAMONDS and card.need_target and not any(((not p.character.check(self.game, chd.ApacheKid) and not any((isinstance(c, grc.Calumet) for c in p.gold_rush_equipment))) for p in self.game.get_alive_players())):
                if isinstance(card, cs.Bang):
                     return True
                else:
                    return len(self.equipment) == 0 # se non ho carte equipaggiamento
            elif (isinstance(card, cs.Bang) or (isinstance(card, cs.Mancato) and self.character.check(self.game, chars.CalamityJanet))) and self.has_played_bang and not any((isinstance(c, cs.Volcanic) for c in self.equipment)) or not any((self.get_sight() >= p['dist'] for p in self.game.get_visible_players(self))):
                return True
            elif isinstance(card, cs.Mancato) or (card.need_with and len(self.hand) < 2):
                return True
            elif isinstance(card, cs.Panico) and not any((self.get_sight(False) >= p['dist'] for p in self.game.get_visible_players(self))) and len(self.equipment) == 0:
                return True
            elif isinstance(card, csd.Pugno) and not any((self.get_sight(False) >= p['dist'] for p in self.game.get_visible_players(self))):
                return True
            elif isinstance(card, cs.Prigione) and not any((not p['is_sheriff'] for p in self.game.get_visible_players(self))):
                return True
            elif not card.is_weapon and any((c.name == card.name for c in self.equipment)):
                return True
            return False
        return True

    def end_turn(self, forced=False):
        print(f"{self.name} wants to end his turn")
        if not self.is_my_turn and not forced:
            return
        maxcards = self.lives if not self.character.check(self.game, chd.SeanMallory) else 10
        if maxcards == self.lives and any((isinstance(c, grc.Cinturone) for c in self.gold_rush_equipment)):
            maxcards = 8
        if len(self.hand) > maxcards and not forced:
            print(f"{self.name}: I have to many cards in my hand and I can't end the turn")
        elif not self.check_can_end_turn():
            print(f"{self.name}: I must play the legge del west card")
        elif self.pending_action == PendingAction.PLAY or forced:
            for i in range(len(self.equipment)):
                if self.equipment[i].usable_next_turn and not self.equipment[i].can_be_used_now:
                    self.equipment[i].can_be_used_now = True
            for i in range(len(self.hand)):
                if self.hand[i].must_be_used:
                    self.hand[i].must_be_used = False
            self.has_played_bang = False
        ##Vendetta##
            if not forced and self.game.check_event(ce.Vendetta) and self.can_play_vendetta:
                picked: cs.Card = self.game.deck.pick_and_scrap()
                G.sio.emit('chat_message', room=self.game.name, data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                if picked.check_suit(self.game, [cs.Suit.HEARTS]):
                    self.play_turn(can_play_vendetta=False)
                    return
        ##Don Bell##
            if not forced and self.character.check(self.game, grch.DonBell) and self.can_play_again_don_bell:
                picked: cs.Card = self.game.deck.pick_and_scrap()
                G.sio.emit('chat_message', room=self.game.name, data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                self.can_play_again_don_bell = False
                if picked.check_suit(self.game, [cs.Suit.HEARTS, cs.Suit.DIAMONDS]):
                    self.play_turn(can_play_vendetta=False)
                    return
        ##Ghost##
            if (self.is_dead and self.is_ghost and self.game.check_event(ceh.CittaFantasma) and not any((True for c in self.equipment if isinstance(c, tvosc.Fantasma)))) or (self.is_dead and forced and self.is_ghost and not any((True for c in self.equipment if isinstance(c, tvosc.Fantasma)))):
                self.is_ghost = False
                for i in range(len(self.hand)):
                    self.game.deck.scrap(self.hand.pop(), True)
                for i in range(len(self.equipment)):
                    self.game.deck.scrap(self.equipment.pop(), True)
            self.is_my_turn = False
            self.can_play_again_don_bell = True
            self.committed_suit_manette = None
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.next_turn()

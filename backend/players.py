from enum import IntEnum
import json
from random import randrange
import socketio
from cards import Mancato

import roles
import cards
import characters

class PendingAction(IntEnum):
    PICK = 0
    DRAW = 1
    PLAY = 2
    RESPOND = 3
    WAIT = 4
    CHOOSE = 5

class Player:
    def __init__(self, name, sid, sio):
        super().__init__()
        self.name = name
        self.sid = sid
        self.sio = sio
        self.hand: cards.Card = []
        self.equipment: cards.Card = []
        self.role: roles.Role = None
        self.character: characters.Character = None
        self.lives = 0
        self.max_lives = 0
        self.game = None
        self.is_my_turn = False
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.pending_action: PendingAction = None
        self.available_characters = []
        self.was_shot = False
        self.on_pick_cb = None
        self.on_failed_response_cb = None
        self.event_type: str = None
        self.expected_response = None
        self.attacker = None
        self.target_p: str  = None

    def join_game(self, game):
        self.game = game
        print(f'I {self.name} joined {self.game}')

    def disconnect(self):
        return self.game.handle_disconnect(self)

    def set_role(self, role: roles.Role):
        self.role = role
        print(f'I {self.name} am a {role.name}, my goal is "{role.goal}"')
        self.sio.emit('role', room=self.sid, data=json.dumps(role, default=lambda o: o.__dict__))

    def set_character(self, character: str):
        print(self.available_characters, character)
        self.character = next(x for x in self.available_characters if x.name==character)
        self.available_characters = []
        print(f'I {self.name} chose character {self.character.name}')
        self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha scelto il personaggio.')
        self.game.notify_character_selection()

    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
        self.hand = []
        self.equipment = []
        self.pending_action = PendingAction.WAIT

    def set_available_character(self, available):
        self.available_characters = available
        print(f'I {self.name} have to choose between {available}')
        self.sio.emit('characters', room=self.sid, data=json.dumps(available, default=lambda o: o.__dict__))

    def notify_self(self):
        if self.lives <= 0 and self.max_lives > 0:
            print('dying, attacker', self.attacker)
            self.game.player_death(self)
        if isinstance(self.character, characters.CalamityJanet):
            self.expected_response = [cards.Mancato(0,0).name, cards.Bang(0,0).name]
        ser = self.__dict__.copy()
        ser.pop('game')
        ser.pop('sio')
        ser.pop('sid')
        ser.pop('on_pick_cb')
        ser.pop('on_failed_response_cb')
        # ser.pop('expected_response')
        ser.pop('attacker')
        ser['sight'] = self.get_sight()
        self.sio.emit('self', room=self.sid, data=json.dumps(ser, default=lambda o: o.__dict__))
        self.sio.emit('self_vis', room=self.sid, data=json.dumps(self.game.get_visible_players(self), default=lambda o: o.__dict__))
        self.game.notify_all()

    def play_turn(self):
        if self.lives == 0:
            self.end_turn(forced=True)
        self.sio.emit('chat_message', room=self.game.name, data=f'È il turno di {self.name}.')
        print(f'I {self.name} was notified that it is my turn')
        self.was_shot = False
        self.is_my_turn = True
        self.is_waiting_for_action = True
        self.has_played_bang = False
        if any([isinstance(c, cards.Dinamite) or isinstance(c, cards.Prigione) for c in self.equipment]):
            self.pending_action = PendingAction.PICK
        else:
            self.pending_action = PendingAction.DRAW
        self.notify_self()

    def draw(self):
        if self.pending_action != PendingAction.DRAW:
            return
        for i in range(2):
            self.hand.append(self.game.deck.draw())
        self.pending_action = PendingAction.PLAY
        self.notify_self()

    def pick(self):
        if self.pending_action != PendingAction.PICK:
            return
        pickable_cards = 1 + self.character.pick_mod
        if self.is_my_turn:
            for i in range(len(self.equipment)):
                if isinstance(self.equipment[i], cards.Dinamite):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cards.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        if picked.suit == cards.Suit.SPADES and 2 <= picked.number <= 9 and pickable_cards == 0:
                            self.lives -= 3
                            self.game.deck.scrap(self.equipment.pop(i))
                            if isinstance(self.character, characters.BartCassidy):
                                self.hand.append(self.game.deck.draw())
                            self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha fatto esplodere la dinamite.')
                            print(f'{self.name} Boom, -3 hp')
                        else:
                            self.game.next_player().equipment.append(self.equipment.pop(i))
                            self.game.next_player().notify_self()
                    if any([isinstance(c, cards.Dinamite) or isinstance(c, cards.Prigione) for c in self.equipment]):
                        self.notify_self()
                        return
            for i in range(len(self.equipment)):
                if isinstance(self.equipment[i], cards.Prigione):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cards.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        if picked.suit != cards.Suit.HEARTS and pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i))
                            self.end_turn(forced=True)
                            return
                        else:
                            self.game.deck.scrap(self.equipment.pop(i))
                            break
                    break
            self.pending_action = PendingAction.DRAW
            self.notify_self()
        else:
            self.pending_action = PendingAction.WAIT
            self.on_pick_cb()

    def get_playable_cards(self):
        playable_cards = []
        for i in range(len(self.hand)):
            card = self.hand[i]
            if isinstance(card, cards.Bang) and self.has_played_bang and not any([isinstance(c, cards.Volcanic) for c in self.equipment]):
                continue
            elif isinstance(card, cards.Birra) and self.lives >= self.max_lives:
                continue
            else:
                playable_cards.append(i)
        return playable_cards

    def get_public_description(self):
        s = f"{self.name} {'Sheriff ⭐️' if isinstance(self.role, roles.Sheriff) else ''} ({self.lives}/{self.max_lives} ⁍) {len(self.hand)} Cards in hand, "
        s += f"equipment {[str(c) for c in self.equipment]}"
        return s

    def play_card(self, hand_index: int, againts=None):
        if not (0 <= hand_index < len(self.hand)):
            print('illegal')
            return
        card: cards.Card = self.hand.pop(hand_index)
        print(self.name, 'is playing ', card, ' against:', againts)
        if isinstance(card, cards.Prigione) and not isinstance(self.game.get_player_named(againts).role, roles.Sheriff):
            self.game.get_player_named(againts).equipment.append(card)
            self.game.get_player_named(againts).notify_self()
        elif card.is_equipment and card.name not in [c.name for c in self.equipment]:
            if card.is_weapon:
                has_weapon = False
                for i in range(len(self.equipment)):
                    if self.equipment[i].is_weapon:
                        self.game.deck.scrap(self.equipment[i])
                        self.equipment[i] = card
                        has_weapon = True
                        break
                if not has_weapon:
                    self.equipment.append(card)
            else:
                self.equipment.append(card)
        else:
            did_play_card = len(self.hand) + 1 > self.lives
            if isinstance(card, cards.Bang) and self.has_played_bang and not any([isinstance(c, cards.Volcanic) for c in self.equipment]) and againts != None:
                self.hand.insert(hand_index, card)
                return
            elif isinstance(card, cards.Bang) and againts != None:
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} contro {againts}.')
                self.has_played_bang = True
                self.game.attack(self, againts)
                did_play_card = True
            elif isinstance(card, cards.Birra) and len(self.game.players) != 2:
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato una {card.name}.')
                self.lives = min(self.lives+1, self.max_lives)
                did_play_card = True
            elif isinstance(card, cards.CatBalou) and againts != None:
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} contro {againts}.')
                self.pending_action = PendingAction.CHOOSE
                self.choose_action = 'discard'
                self.target_p = againts
                did_play_card = True
                print('choose now')
            elif isinstance(card, cards.Diligenza):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} e ha pescato 2 carte.')
                for i in range(2):
                    self.hand.append(self.game.deck.draw())
                did_play_card = True
            elif isinstance(card, cards.Duello):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} contro {againts}.')
                self.game.duel(self, againts)
                did_play_card = True
            elif isinstance(card, cards.Emporio):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name}.')
                self.game.emporio()
                did_play_card = True
            elif isinstance(card, cards.Gatling):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name}.')
                self.game.attack_others(self)
                did_play_card = True
            elif isinstance(card, cards.Indiani):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name}.')
                self.game.indian_others(self)
                did_play_card = True
            elif isinstance(card, cards.Mancato):
                pass
            elif isinstance(card, cards.Panico):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} contro {againts}.')
                self.pending_action = PendingAction.CHOOSE
                self.choose_action = 'steal'
                self.target_p = againts
                print('choose now')
                did_play_card = True
            elif isinstance(card, cards.Saloon):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} e ha curato 1 punto vita a tutti.')
                for p in self.game.players:
                    p.lives = min(p.lives+1, p.max_lives)
                    p.notify_self()
                did_play_card = True
            elif isinstance(card, cards.WellsFargo):
                self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha giocato {card.name} e ha pescato 3 carte.')
                for i in range(3):
                    self.hand.append(self.game.deck.draw())
                did_play_card = True
            if did_play_card:
                self.game.deck.scrap(card)
            else:
                self.hand.insert(hand_index, card)
        self.notify_self()

    def choose(self, card_index):
        if self.pending_action != PendingAction.CHOOSE:
            return
        if self.target_p and self.target_p != '':
            target = self.game.get_player_named(self.target_p)
            card = None
            if card_index >= len(target.hand):
                card = target.equipment.pop(card_index - len(target.hand))
            else:
                card = target.hand.pop(card_index)
            target.notify_self()
            if self.choose_action == 'steal':
                self.hand.append(card)
            else:
                self.game.deck.scrap(card)
            self.target_p = ''
            self.choose_action = ''
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        else:
            self.game.respond_emporio(self, card_index)

    def barrel_pick(self):
        pickable_cards = 1 + self.character.pick_mod
        if len([c for c in self.equipment if isinstance(c, cards.Barile)]) > 0 and isinstance(self.character, characters.Jourdonnais):
            pickable_cards = 2
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cards.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha estratto {picked}.')
            if picked.suit == cards.Suit.HEARTS:
                self.notify_self()
                self.game.responders_did_respond()
                return
        if len([c for c in self.hand if isinstance(c, cards.Mancato) or (isinstance(self.character, characters.CalamityJanet) and isinstance(c, cards.Bang))]) == 0:
            self.take_damage_response()
            self.game.responders_did_respond()
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cards.Mancato(0,0).name]
            self.on_failed_response_cb = self.take_damage_response
            self.notify_self()

    def get_banged(self, attacker):
        self.attacker = attacker
        if len([c for c in self.hand if isinstance(c, cards.Mancato)]) == 0 and len([c for c in self.equipment if isinstance(c, cards.Barile)]) == 0:
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            if len([c for c in self.equipment if isinstance(c, cards.Barile)]) > 0 or isinstance(self.character, characters.Jourdonnais):
                print('has barrel')
                self.pending_action = PendingAction.PICK
                self.on_pick_cb = self.barrel_pick
            else:
                print('has mancato')
                self.pending_action = PendingAction.RESPOND
                self.expected_response = [cards.Mancato(0,0).name]
                self.on_failed_response_cb = self.take_damage_response
            self.notify_self()
            return True

    def get_indians(self, attacker):
        self.attacker = attacker
        if len([c for c in self.hand if isinstance(c, cards.Bang)]) == 0:
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            print('has bang')
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cards.Bang(0,0).name]
            self.event_type = 'indians'
            self.on_failed_response_cb = self.take_damage_response
            self.notify_self()
            return True

    def get_dueled(self, attacker):
        self.attacker = attacker
        if len([c for c in self.hand if isinstance(c, cards.Bang)]) == 0:
            print('Cant defend')
            self.take_damage_response()
            self.game.responders_did_respond_resume_turn()
            return False
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cards.Bang(0,0).name]
            self.event_type = 'duel'
            self.on_failed_response_cb = self.take_damage_response
            self.notify_self()
            return True

    def take_damage_response(self):
        self.lives -= 1
        if self.lives > 0:
            if isinstance(self.character, characters.BartCassidy):
                self.hand.append(self.game.deck.draw())
            elif isinstance(self.character, characters.ElGringo) and self.attacker and len(self.attacker.hand) > 0:
                self.hand.append(self.attacker.hand.pop(randrange(0, len(self.attacker.hand))))
                self.attacker.notify_self()
        self.notify_self()
        self.attacker = None

    def respond(self, hand_index):
        self.pending_action = PendingAction.WAIT
        if hand_index != -1 and self.hand[hand_index].name == self.expected_response:
            self.game.deck.scrap(self.hand.pop(hand_index))
            self.notify_self()
            if self.event_type == 'duel':
                self.game.duel(self, self.attacker.name)
            else:
                self.game.responders_did_respond_resume_turn()
            self.event_type = ''
        else:
            self.on_failed_response_cb()
            self.game.responders_did_respond_resume_turn()
        self.attacker = None

    def get_sight(self):
        aim = 0
        range = 0
        for card in self.equipment:
            if card.is_weapon:
                range += card.range
            else:
                aim += card.sight_mod
        return max(1, range) + aim + self.character.sight_mod

    def get_visibility(self):
        covers = 0
        for card in self.equipment:
            covers += card.vis_mod
        return self.character.visibility_mod + covers

    def end_turn(self, forced=False):
        if not self.is_my_turn: return
        if len(self.hand) > self.max_lives and not forced:
            print(f"I {self.name} have to many cards in my hand and I can't end the turn")
        else:
            self.is_my_turn = False
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.next_turn()

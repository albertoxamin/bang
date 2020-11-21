from enum import IntEnum
import json
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
        self.on_response_cb = None
        self.expected_response = None

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

    def set_available_character(self, available):
        self.available_characters = available
        print(f'I {self.name} have to choose between {available}')
        self.sio.emit('characters', room=self.sid, data=json.dumps(available, default=lambda o: o.__dict__))

    def notify_self(self):
        ser = self.__dict__.copy()
        ser.pop('game')
        ser.pop('sio')
        ser.pop('sid')
        ser.pop('on_pick_cb')
        ser.pop('on_response_cb')
        ser.pop('expected_response')
        self.sio.emit('self', room=self.sid, data=json.dumps(ser, default=lambda o: o.__dict__))
        self.sio.emit('self_vis', room=self.sid, data=json.dumps(self.game.get_visible_players(self), default=lambda o: o.__dict__))

    def play_turn(self):
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
                        else:
                            break
                    break
            self.pending_action = PendingAction.DRAW
            self.notify_self()
        else:
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
        if card.is_equipment and card.name not in [c.name for c in self.equipment]:
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
            if isinstance(card, cards.Bang) and self.has_played_bang and not any([isinstance(c, cards.Volcanic) for c in self.equipment]):
                return
            if isinstance(card, cards.Bang) and againts != None:
                self.game.attack(self, againts)
            self.game.deck.scrap(card)
        self.notify_self()

    def barrel_pick(self):
        pickable_cards = 1 + self.character.pick_mod
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cards.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            if picked.suit == cards.Suit.HEARTS:
                self.pending_action = PendingAction.WAIT
                self.notify_self()
                self.game.responders_did_respond()
                return
        if len([c for c in self.hand if isinstance(c, cards.Mancato)]) == 0:
            self.take_damage_response()
            self.game.responders_did_respond()
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = cards.Mancato
            self.on_response_cb = self.take_damage_response()
            self.notify_self()

    def get_banged(self):
        if len([c for c in self.hand if isinstance(c, cards.Mancato) or isinstance(c, cards.Barile)]) == 0:
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            if len([c for c in self.hand if isinstance(c, cards.Barile)]) > 0:
                print('has barrel')
                self.pending_action = PendingAction.PICK
                self.on_pick_cb = self.barrel_pick
            else:
                print('has mancato')
                self.pending_action = PendingAction.RESPOND
                self.expected_response = cards.Mancato
                self.on_response_cb = self.take_damage_response()
            self.notify_self()
            return True
    
    def take_damage_response(self):
        self.lives -= 1
        self.notify_self()

    def respond(self, hand_index):
        self.pending_action = PendingAction.WAIT
        if hand_index != -1 and isinstance(self.hand[hand_index], self.expected_response):
            self.game.deck.scrap(self.hand.pop(hand_index))
            self.notify_self()
            self.game.responders_did_respond()
        else:
            self.on_response_cb()
            self.game.responders_did_respond()

    def get_sight(self):
        aim = 0
        for card in self.equipment:
            aim += card.sight_mod
            if card.is_weapon:
                aim += card.range
        return 1 + self.character.sight_mod + aim

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
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.next_turn()

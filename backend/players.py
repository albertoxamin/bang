from enum import IntEnum
import json
import socketio

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

    def join_game(self, game):
        self.game = game
        print(f'I {self.name} joined {self.game}')

    def disconnect(self):
        return self.game.handle_disconnect(self)

    def set_role(self, role: roles.Role):
        self.role = role
        print(f'I {self.name} am a {role.name}, my goal is "{role.goal}"')

    def set_character(self, character: str):
        print(self.available_characters, character)
        self.character = next(x for x in self.available_characters if x.name==character)
        self.available_characters = []
        print(f'I {self.name} chose character {self.character.name}')
        self.sio.emit('chat_message', room=self.game.name, data=f'{self.name} ha scelto il personaggio.')

    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
        self.hand = []
        self.equipment = []

    def set_available_character(self, available):
        self.available_characters = available
        print(f'I {self.name} have to choose between {available}')
        self.sio.emit('characters', room=self.sid, data=json.dumps(available, default=lambda o: o.__dict__))

    def play_turn(self):
        print(f'I {self.name} was notified that it is my turn')
        self.was_shot = False
        self.is_my_turn = True
        self.is_waiting_for_action = True
        self.has_played_bang = False
        if any([isinstance(c) == cards.Dinamite or isinstance(c) == cards.Prigione for c in self.equipment]):
            self.pending_action = PendingAction.PICK

        # # print(f'lives: {self.lives}/{self.max_lives} hand: {[str(c) for c in self.hand]}')
        # print(f'I {self.name} can see {[p.get_public_description() for p in self.game.get_visible_players(self)]}')
        # ser = self.__dict__.copy()
        # ser.pop('game')
        # print(json.dumps(ser, default=lambda o: o.__dict__, indent=4))
    def draw(self):
        for i in range(2):
            self.hand.append(self.game.deck.draw())
        self.pending_action = PendingAction.PLAY

    def pick(self):
        pickable_cards = 1 + self.character.pick_mod
        for i in range(len(self.equipment)):
            if isinstance(self.equipment[i]) == cards.Dinamite:
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
                if any([isinstance(c) == cards.Dinamite or isinstance(c) == cards.Prigione for c in self.equipment]):
                    return
        for i in range(len(self.equipment)):
            if isinstance(self.equipment[i]) == cards.Prigione:
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

    def get_playable_cards(self):
        playable_cards = []
        for i in range(len(self.hand)):
            card = self.hand[i]
            if isinstance(card) == cards.Bang and self.has_played_bang and not any([isinstance(c) == cards.Volcanic for c in self.equipment]):
                continue
            elif isinstance(card) == cards.Birra and self.lives >= self.max_lives:
                continue
            else:
                playable_cards.append(i)
        return playable_cards

    def get_public_description(self):
        s = f"{self.name} {'Sheriff ⭐️' if isinstance(self.role) == roles.Sheriff else ''} ({self.lives}/{self.max_lives} ⁍) {len(self.hand)} Cards in hand, "
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
                for i in range(len(self.equipment)):
                    if self.equipment[i].is_weapon:
                        self.game.deck.scrap(self.equipment[i])
                        self.equipment[i] = card
                        break
            else:
                self.equipment.append(card)
        else:
            if isinstance(card) == cards.Bang and self.has_played_bang and not any([isinstance(c) == cards.Volcanic for c in self.equipment]):
                print('you retard')
            self.game.deck.scrap(card)

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
        if len(self.hand) > self.max_lives and not forced:
            print(f"I {self.name} have to many cards in my hand and I can't end the turn")
        else:
            self.game.next_turn()

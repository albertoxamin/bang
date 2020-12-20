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
import eventlet

class PendingAction(IntEnum):
    PICK = 0
    DRAW = 1
    PLAY = 2
    RESPOND = 3
    WAIT = 4
    CHOOSE = 5

class Player:

    def __init__(self, name, sid, sio, bot=False):
        import bang.game as g
        super().__init__()
        self.name = name
        self.sid = sid
        self.sio = sio
        self.hand: cs.Card = []
        self.equipment: cs.Card = []
        self.role: r.Role = None
        self.character: chars.Character = None
        self.real_character: chars.Character = None
        self.lives = 0
        self.max_lives = 0
        self.game: g = None
        self.is_my_turn = False
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.pending_action: PendingAction = None
        self.available_characters = []
        self.was_shot = False
        self.on_pick_cb = None
        self.on_failed_response_cb = None
        self.event_type: str = None
        self.expected_response = []
        self.attacker: Player = None
        self.target_p: str = None
        self.is_drawing = False
        self.is_giving_life = False
        self.mancato_needed = 0
        self.molly_discarded_cards = 0
        self.is_bot = bot
        self.special_use_count = 0

    def reset(self):
        self.hand: cs.Card = []
        self.equipment: cs.Card = []
        self.role: r.Role = None
        self.character: chars.Character = None
        self.real_character: chars.Character = None
        self.lives = 0
        self.max_lives = 0
        self.is_my_turn = False
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.pending_action: PendingAction = None
        self.available_characters = []
        self.was_shot = False
        self.on_pick_cb = None
        self.on_failed_response_cb = None
        self.event_type: str = None
        self.expected_response = []
        self.attacker: Player = None
        self.target_p: str = None
        self.is_drawing = False
        self.special_use_count = 0
        try:
            del self.win_status
        except:
            pass
        self.mancato_needed = 0
        self.molly_discarded_cards = 0

    def join_game(self, game):
        self.game = game
        print(f'I {self.name} joined {self.game}')

    def disconnect(self):
        return self.game.handle_disconnect(self)

    def set_role(self, role: r.Role):
        self.role = role
        print(f'I {self.name} am a {role.name}, my goal is "{role.goal}"')
        self.sio.emit('role', room=self.sid, data=json.dumps(
            role, default=lambda o: o.__dict__))

    def set_character(self, character: str):
        print(self.available_characters, character)
        if self.character == None:
            self.character = next(
                x for x in self.available_characters if x.name == character)
            self.real_character = self.character
            self.available_characters = []
            print(f'I {self.name} chose character {self.character.name}')
            self.sio.emit('chat_message', room=self.game.name,
                        data=f'_did_choose_character|{self.name}')
            self.game.notify_character_selection()
        elif self.real_character and isinstance(self.real_character, chd.VeraCuster):
            self.character = next(
                x for x in self.available_characters if x.name == character)
            self.available_characters = []
            self.sio.emit('chat_message', room=self.game.name,
                        data=f'_did_choose_character|{self.name}')
            self.pending_action = PendingAction.DRAW
            self.notify_self()


    def prepare(self):
        self.max_lives = self.character.max_lives + self.role.health_mod
        self.lives = self.max_lives
        self.hand = []
        self.equipment = []
        self.pending_action = PendingAction.WAIT

    def set_available_character(self, available):
        self.available_characters = available
        print(f'I {self.name} have to choose between {available}')
        if not self.is_bot:
            self.sio.emit('characters', room=self.sid, data=json.dumps(
                available, default=lambda o: o.__dict__))
        else:
            self.set_character(available[randrange(0, len(available))].name)

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
        self.sio.emit('notify_card', room=self.sid, data=mess)

    def notify_self(self):
        if self.pending_action == PendingAction.DRAW and self.game.check_event(ce.Peyote):
            self.available_cards = [{
                'icon': '🔴'
            },{
                'icon': '⚫'
            }]
            self.is_drawing = True
            self.pending_action = PendingAction.CHOOSE
        if isinstance(self.character, chars.CalamityJanet):
            if cs.Mancato(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Mancato(0, 0).name)
            elif cs.Bang(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Bang(0, 0).name)
        elif isinstance(self.character, chars.SuzyLafayette) and len(self.hand) == 0:
            self.hand.append(self.game.deck.draw())
        ser = self.__dict__.copy()
        ser.pop('game')
        ser.pop('sio')
        ser.pop('sid')
        ser.pop('on_pick_cb')
        ser.pop('on_failed_response_cb')
        # ser.pop('expected_response')
        ser.pop('attacker')
        if self.attacker:
            ser['attacker'] = self.attacker.name
        ser['sight'] = self.get_sight()
        ser['lives'] = max(ser['lives'], 0)

        if self.lives <= 0 and self.max_lives > 0:
            print('dying, attacker', self.attacker)
            if isinstance(self.character, chars.SidKetchum) and len(self.hand) > 1:
                self.lives += 1
                self.game.deck.scrap(self.hand.pop(
                    randrange(0, len(self.hand))))
                self.game.deck.scrap(self.hand.pop(
                    randrange(0, len(self.hand))))
        if self.lives <= 0 and self.max_lives > 0:
            self.pending_action = PendingAction.WAIT
            ser['hand'] = []
            ser['equipment'] = []
            self.sio.emit('self', room=self.sid, data=json.dumps(
                ser, default=lambda o: o.__dict__))
            self.game.player_death(self)
        elif not self.is_bot:
            self.sio.emit('self_vis', room=self.sid, data=json.dumps(
            self.game.get_visible_players(self), default=lambda o: o.__dict__))
        if not self.is_bot:
            self.sio.emit('self', room=self.sid, data=json.dumps(
                ser, default=lambda o: o.__dict__))
            self.game.notify_all()
        else:
            self.game.notify_all()
            self.bot_logic()
            self.game.notify_all()

    def bot_logic(self):
        if self.game.shutting_down: return
        if self.pending_action != None and self.pending_action != PendingAction.WAIT:
            eventlet.sleep(uniform(0.6, 1.5))
        else:
            return
        if self.pending_action == PendingAction.PICK:
            self.pick()
        elif self.pending_action == PendingAction.DRAW:
            self.draw('')
        elif self.pending_action == PendingAction.PLAY:
            has_played = False
            if len([c for c in self.hand if (c.is_equipment or c.usable_next_turn) and not self.game.check_event(ce.IlGiudice)]) > 0:
                for i in range(len(self.hand)):
                    if self.hand[i].is_equipment or self.hand[i].usable_next_turn:
                        self.play_card(i)
                        has_played = True
                        break
            elif any([isinstance(c, cs.WellsFargo) or isinstance(c, cs.Diligenza) or isinstance(c, cs.Emporio) or isinstance(c, cs.Birra)  for c in self.hand]):
                for i in range(len(self.hand)):
                    c = self.hand[i]
                    if isinstance(c, cs.WellsFargo) or isinstance(c, cs.Diligenza) or isinstance(c, cs.Emporio) or (isinstance(c, cs.Birra) and self.lives < self.max_lives):
                        self.play_card(i)
                        has_played = True
                        break
            elif len([c for c in self.hand if c.need_target and not (self.has_played_bang and not any([isinstance(c, cs.Volcanic) for c in self.equipment]))]) > 0:
                for i in range(len(self.hand)):
                    if self.hand[i].need_target and not (self.has_played_bang and not any([isinstance(c, cs.Volcanic) for c in self.equipment])):
                        if self.hand[i].need_with and len(self.hand) < 2:
                            continue
                        _range = self.get_sight() if self.hand[i].name == 'Bang!' or self.hand[i].name == "Pepperbox" else self.hand[i].range
                        others = [p for p in self.game.get_visible_players(self) if _range >= p['dist'] and not (isinstance(self.role, r.Vice) and p['is_sheriff'])]
                        if len(others) == 0:
                            continue
                        target = others[randrange(0, len(others))]
                        if target['is_sheriff'] and isinstance(self.role, r.Renegade):
                            target = others[randrange(0, len(others))]
                        if not self.hand[i].need_with:
                            self.play_card(i, against=target['name'])
                        else:
                            self.play_card(i, against=target['name'], _with=sample([j for j in range(len(self.hand)) if j != i], 1)[0])
                        has_played = True
                        break
            elif any([not isinstance(c, cs.Mancato) and c.usable_next_turn and c.can_be_used_now for c in self.equipment]):
                print('hmm', [not isinstance(c, cs.Mancato) and c.usable_next_turn and c.can_be_used_now for c in self.equipment])
                for i in range(len(self.equipment)):
                    c = self.equipment[i]
                    if not isinstance(c, cs.Mancato) and c.usable_next_turn and c.can_be_used_now:
                        if not c.need_target:
                            self.play_card(len(self.hand)+i)
                        else:
                            _range = self.get_sight() if c.name == "Pepperbox" else c.range
                            others = [p for p in self.game.get_visible_players(self) if _range >= p['dist'] and not (isinstance(self.role, r.Vice) and p['is_sheriff'])]
                            if len(others) == 0:
                                continue
                            target = others[randrange(0, len(others))]
                            if target['is_sheriff'] and isinstance(self.role, r.Renegade):
                                target = others[randrange(0, len(others))]
                            self.play_card(len(self.hand)+i, against=target['name'])
                        has_played = True
                        break
            maxcards = self.lives if not isinstance(self.character, chd.SeanMallory) else 10
            if not has_played and len(self.hand) > maxcards:
                self.scrap(0)
            else:
                self.end_turn()
        elif self.pending_action == PendingAction.RESPOND:
            did_respond = False
            for i in range(len(self.hand)):
                if self.hand[i].name in self.expected_response:
                    self.respond(i)
                    did_respond = True
                    break
            for i in range(len(self.equipment)):
                if not self.game.check_event(ce.Lazo) and self.equipment[i].name in self.expected_response:
                    self.respond(len(self.hand)+i)
                    did_respond = True
                    break
            if not did_respond:
                self.respond(-1)
        elif self.pending_action == PendingAction.CHOOSE:
            if not self.target_p:
                self.choose(randrange(0, len(self.available_cards)))
            else:
                target = self.game.get_player_named(self.target_p)
                if len(target.hand)+len(target.equipment) == 0:
                    self.pending_action = PendingAction.PLAY
                    self.notify_self()
                else:
                    self.choose(randrange(0, len(target.hand)+len(target.equipment)))

    def play_turn(self):
        if self.lives == 0:
            return self.end_turn(forced=True)
        self.scrapped_cards = 0
        self.sio.emit('chat_message', room=self.game.name,
                      data=f'_turn|{self.name}')
        print(f'I {self.name} was notified that it is my turn')
        self.was_shot = False
        self.is_my_turn = True
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.special_use_count = 0
        if self.game.check_event(ce.FratelliDiSangue) and self.lives > 1 and not self.is_giving_life and len([p for p in self.game.players if p != self and p.lives < p.max_lives]):
            self.available_cards = [{
                'name': p.name,
                'icon': isinstance(p.role, r.Sheriff),
            } for p in self.game.players if p != self and p.lives < p.max_lives]
            self.available_cards.append({'icon': '❌'})
            self.pending_action = PendingAction.CHOOSE
            self.is_giving_life = True
        elif not self.game.check_event(ce.Lazo) and any([isinstance(c, cs.Dinamite) or isinstance(c, cs.Prigione) for c in self.equipment]):
            self.is_giving_life = False
            self.pending_action = PendingAction.PICK
        else:
            self.is_giving_life = False
            if isinstance(self.real_character, chd.VeraCuster):
                self.set_available_character([p.character for p in self.game.players if p != self])
            else:
                self.pending_action = PendingAction.DRAW
        self.notify_self()

    def draw(self, pile):
        if self.pending_action != PendingAction.DRAW:
            return
        if pile == 'event' and self.lives < self.max_lives and self.game.check_event(ce.LiquoreForte):
            self.lives += 1
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif isinstance(self.character, chars.KitCarlson):
            self.is_drawing = True
            self.available_cards = [self.game.deck.draw() for i in range(3)]
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        elif isinstance(self.character, chd.PatBrennan) and type(pile) == str and pile != self.name and pile in self.game.players_map and len(self.game.get_player_named(pile).equipment) > 0:
            self.is_drawing = True
            self.available_cards = self.game.get_player_named(pile).equipment
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        else:
            self.pending_action = PendingAction.PLAY
            if pile == 'scrap' and isinstance(self.character, chars.PedroRamirez):
                self.hand.append(self.game.deck.draw_from_scrap_pile())
                self.hand.append(self.game.deck.draw())
                self.sio.emit('chat_message', room=self.game.name,
                              data=f'_draw_from_scrap|{self.name}')
            elif type(pile) == str and pile != self.name and pile in self.game.players_map and isinstance(self.character, chars.JesseJones) and len(self.game.get_player_named(pile).hand) > 0:
                self.hand.append(self.game.get_player_named(pile).hand.pop(
                    randrange(0, len(self.game.get_player_named(pile).hand))))
                self.game.get_player_named(pile).notify_self()
                self.sio.emit('chat_message', room=self.game.name,
                              data=f'_draw_from_player|{self.name}|{pile}')
                self.hand.append(self.game.deck.draw())
            elif isinstance(self.character, chd.BillNoface):
                self.hand.append(self.game.deck.draw())
                for i in range(self.max_lives-self.lives):
                    self.hand.append(self.game.deck.draw())
            else:
                for i in range(2):
                    card: cs.Card = self.game.deck.draw()
                    self.hand.append(card)
                    if i == 1 and isinstance(self.character, chars.BlackJack) or self.game.check_event(ce.LeggeDelWest):
                        for p in self.game.players:
                            if p != self:
                                p.notify_card(self, card, 'blackjack_special' if isinstance(self.character, chars.BlackJack) else 'foc.leggedelwest')
                        if card.suit == cs.Suit.HEARTS or card.suit == cs.Suit.DIAMONDS and isinstance(self.character, chars.BlackJack):
                            self.hand.append(self.game.deck.draw())
                if isinstance(self.character, chd.PixiePete):
                    self.hand.append(self.game.deck.draw())
            self.notify_self()

    def pick(self):
        if self.pending_action != PendingAction.PICK:
            return
        pickable_cards = 1 + self.character.pick_mod
        if self.is_my_turn:
            for i in range(len(self.equipment)):
                if isinstance(self.equipment[i], cs.Dinamite):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cs.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        self.sio.emit('chat_message', room=self.game.name,
                                      data=f'_flipped|{self.name}|{picked}')
                        if picked.suit == cs.Suit.SPADES and 2 <= picked.number <= 9 and pickable_cards == 0:
                            self.lives -= 3
                            self.game.deck.scrap(self.equipment.pop(i))
                            self.sio.emit('chat_message', room=self.game.name,
                                          data=f'_explode|{self.name}')
                            if isinstance(self.character, chars.BartCassidy) and self.lives > 0:
                                for i in range(3):
                                    self.hand.append(self.game.deck.draw())
                                self.sio.emit('chat_message', room=self.game.name,
                                              data=f'_special_bart_cassidy|{self.name}')
                            print(f'{self.name} Boom, -3 hp')
                            break
                        else:
                            self.game.next_player().equipment.append(self.equipment.pop(i))
                            self.game.next_player().notify_self()
                            break
                    if any([isinstance(c, cs.Dinamite) or isinstance(c, cs.Prigione) for c in self.equipment]):
                        self.notify_self()
                        return
            for i in range(len(self.equipment)):
                if isinstance(self.equipment[i], cs.Prigione):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cs.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        self.sio.emit('chat_message', room=self.game.name,
                                      data=f'_flipped|{self.name}|{picked}')
                        if picked.suit != cs.Suit.HEARTS and pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i))
                            self.end_turn(forced=True)
                            return
                        elif pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i))
                            break
                    break
            if any([isinstance(c, cs.Prigione) for c in self.equipment]):
                self.notify_self()
                return
            if isinstance(self.real_character, chd.VeraCuster):
                self.set_available_character([p.character for p in self.game.players if p != self])
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
            if isinstance(card, cs.Bang) and self.has_played_bang and not any([isinstance(c, cs.Volcanic) for c in self.equipment]):
                continue
            elif isinstance(card, cs.Birra) and self.lives >= self.max_lives:
                continue
            else:
                playable_cards.append(i)
        return playable_cards

    def get_public_description(self):
        s = f"{self.name} {'Sheriff ⭐️' if isinstance(self.role, r.Sheriff) else ''} ({self.lives}/{self.max_lives} ⁍) {len(self.hand)} Cards in hand, "
        s += f"equipment {[str(c) for c in self.equipment]}"
        return s

    def play_card(self, hand_index: int, against=None, _with=None):
        if not self.is_my_turn or self.pending_action != PendingAction.PLAY:
            return
        if not (0 <= hand_index < len(self.hand) + len(self.equipment)):
            return
        card: cs.Card = self.hand.pop(hand_index) if hand_index < len(self.hand) else self.equipment.pop(hand_index-len(self.hand))
        withCard: cs.Card = None
        if _with != None:
            withCard = self.hand.pop(_with) if hand_index > _with else self.hand.pop(_with - 1)
        print(self.name, 'is playing ', card, ' against:', against, ' with:', _with)
        did_play_card = False
        event_blocks_card = (self.game.check_event(ce.IlGiudice) and (card.is_equipment or (card.usable_next_turn and not card.can_be_used_now))) or (self.game.check_event(ce.Lazo) and card.usable_next_turn and card.can_be_used_now)
        if not(against != None and isinstance(self.game.get_player_named(against).character, chd.ApacheKid) and card.suit == cs.Suit.DIAMONDS) and not event_blocks_card:
            did_play_card = card.play_card(self, against, withCard)
        if not card.is_equipment and not card.usable_next_turn or event_blocks_card:
            if did_play_card:
                self.game.deck.scrap(card)
            else:
                self.hand.insert(hand_index, card)
                if withCard:
                    self.hand.insert(_with, withCard)
        elif card.usable_next_turn and card.can_be_used_now:
            if did_play_card:
                self.game.deck.scrap(card)
            else:
                self.equipment.insert(hand_index-len(self.hand), card)
        self.notify_self()

    def choose(self, card_index):
        if self.pending_action != PendingAction.CHOOSE:
            return
        if self.target_p and self.target_p != '':  # panico, cat balou
            target = self.game.get_player_named(self.target_p)
            card = None
            if card_index >= len(target.hand):
                card = target.equipment.pop(card_index - len(target.hand))
            else:
                card = target.hand.pop(card_index)
            target.notify_self()
            if self.choose_action == 'steal':
                if card.usable_next_turn:
                    card.can_be_used_now = False
                self.hand.append(card)
            else:
                self.game.deck.scrap(card)
            if self.event_type != 'rissa' or (self.event_type == 'rissa' and self.target_p == [p.name for p in self.game.players if p != self and (len(p.hand)+len(p.equipment)) > 0][-1]):
                self.event_type = ''
                self.target_p = ''
                self.choose_action = ''
                self.pending_action = PendingAction.PLAY
            else:
                self.target_p = self.game.players[self.game.players_map[self.target_p]+1].name
                while self.target_p == self.name or len(self.game.players[self.game.players_map[self.target_p]].hand) + len(self.game.players[self.game.players_map[self.target_p]].equipment) == 0:
                    self.target_p = self.game.players[self.game.players_map[self.target_p]+1].name
            self.notify_self()
        elif self.is_giving_life and self.game.check_event(ce.FratelliDiSangue):
            try:
                player = self.game.get_player_named(self.available_cards[card_index]['name'])
                player.lives += 1
                self.lives -= 1
                player.notify_self()
                self.sio.emit('chat_message', room=self.game.name, data=f'_fratelli_sangue|{self.name}|{player.name}')
            except: pass
            self.play_turn()
        elif self.is_drawing and self.game.check_event(ce.Peyote):
            self.is_drawing = False
            card = self.game.deck.draw()
            self.hand.append(card)
            self.sio.emit('chat_message', room=self.game.name, data=f"_guess|{self.name}|{self.available_cards[card_index]['icon']}")
            self.available_cards = []
            if card_index == card.suit%2:
                self.sio.emit('chat_message', room=self.game.name, data=f"_guess_right|{self.name}")
                self.pending_action = PendingAction.DRAW
            else:
                self.sio.emit('chat_message', room=self.game.name, data=f"_guess_wrong|{self.name}")
                self.pending_action = PendingAction.PLAY
            self.notify_self()
        # specifico per personaggio
        elif self.is_drawing and isinstance(self.character, chars.KitCarlson):
            self.hand.append(self.available_cards.pop(card_index))
            if len(self.available_cards) == 1:
                self.game.deck.put_on_top(self.available_cards.pop())
                self.is_drawing = False
                self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.is_drawing and isinstance(self.character, chd.PatBrennan):
            card = self.available_cards.pop(card_index)
            if card.usable_next_turn:
                card.can_be_used_now = False
            self.hand.append(card)
            self.available_cards = []
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        else:  # emporio
            self.game.respond_emporio(self, card_index)

    def barrel_pick(self):
        pickable_cards = 1 + self.character.pick_mod
        if len([c for c in self.equipment if isinstance(c, cs.Barile)]) > 0 and isinstance(self.character, chars.Jourdonnais):
            pickable_cards = 2
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cs.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            self.sio.emit('chat_message', room=self.game.name,
                            data=f'_flipped|{self.name}|{picked}')
            if picked.suit == cs.Suit.HEARTS:
                self.mancato_needed -= 1
                self.notify_self()
                if self.mancato_needed <= 0:
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                    return
        if not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Mancato) or (isinstance(self.character, chars.CalamityJanet) and isinstance(c, cs.Bang)) or isinstance(self.character, chd.ElenaFuente)]) == 0\
             and len([c for c in self.equipment if c.can_be_used_now and isinstance(c, cs.Mancato)]) == 0:
            self.take_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = self.game.deck.mancato_cards
            if isinstance(self.character, chd.ElenaFuente):
                self.expected_response = self.game.deck.all_cards_str
            self.on_failed_response_cb = self.take_damage_response
            self.notify_self()

    def get_banged(self, attacker, double=False):
        self.attacker = attacker
        self.mancato_needed = 1 if not double else 2
        for i in range(len(self.equipment)):
            if self.equipment[i].can_be_used_now:
                print('usable', self.equipment[i])
        if not self.game.is_competitive and len([c for c in self.equipment if isinstance(c, cs.Barile)]) == 0 and not isinstance(self.character, chars.Jourdonnais)\
             and len([c for c in self.hand if isinstance(c, cs.Mancato) or (isinstance(self.character, chars.CalamityJanet) and isinstance(c, cs.Bang)) or isinstance(self.character, chd.ElenaFuente)]) == 0\
             and len([c for c in self.equipment if c.can_be_used_now and isinstance(c, cs.Mancato)]) == 0:
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            if (not self.game.check_event(ce.Lazo) and len([c for c in self.equipment if isinstance(c, cs.Barile)]) > 0) or isinstance(self.character, chars.Jourdonnais):
                print('has barrel')
                self.pending_action = PendingAction.PICK
                self.on_pick_cb = self.barrel_pick
            else:
                print('has mancato')
                self.pending_action = PendingAction.RESPOND
                self.expected_response = self.game.deck.mancato_cards
                if self.attacker and self.attacker in self.game.players and isinstance(self.attacker.character, chd.BelleStar) or self.game.check_event(ce.Lazo):
                    self.expected_response = self.game.deck.mancato_cards_not_green
                if isinstance(self.character, chd.ElenaFuente):
                    self.expected_response = self.game.deck.all_cards_str
                self.on_failed_response_cb = self.take_damage_response
            return True

    def get_indians(self, attacker):
        self.attacker = attacker
        if not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Bang) or (isinstance(self.character, chars.CalamityJanet) and isinstance(c, cs.Mancato))]) == 0:
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            print('has bang')
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cs.Bang(0, 0).name]
            self.event_type = 'indians'
            self.on_failed_response_cb = self.take_damage_response
            return True

    def get_dueled(self, attacker):
        self.attacker = attacker
        if not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Bang) or (isinstance(self.character, chars.CalamityJanet) and isinstance(c, cs.Mancato))]) == 0:
            print('Cant defend')
            self.take_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
            return False
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cs.Bang(0, 0).name]
            self.event_type = 'duel'
            self.on_failed_response_cb = self.take_damage_response
            return True

    def take_damage_response(self):
        self.lives -= 1
        if self.lives > 0:
            if isinstance(self.character, chars.BartCassidy):
                self.sio.emit('chat_message', room=self.game.name,
                                data=f'_special_bart_cassidy|{self.name}')
                self.hand.append(self.game.deck.draw())
            elif isinstance(self.character, chars.ElGringo) and self.attacker and len(self.attacker.hand) > 0:
                self.hand.append(self.attacker.hand.pop(
                    randrange(0, len(self.attacker.hand))))
                self.sio.emit('chat_message', room=self.game.name,
                              data=f'_special_el_gringo|{self.name}|{self.attacker.name}')
                self.attacker.notify_self()
        while self.lives <= 0 and len(self.game.players) > 2 and len([c for c in self.hand if isinstance(c, cs.Birra)]) > 0:
            for i in range(len(self.hand)):
                if isinstance(self.hand[i], cs.Birra):
                    if isinstance(self.character, chd.MollyStark) and not self.is_my_turn:
                        self.hand.append(self.game.deck.draw())
                    self.lives += 1
                    self.game.deck.scrap(self.hand.pop(i))
                    self.sio.emit('chat_message', room=self.game.name,
                                  data=f'_beer_save|{self.name}')
                    break
        self.mancato_needed = 0
        self.event_type = ''
        self.notify_self()
        self.attacker = None

    def respond(self, hand_index):
        if self.pending_action != PendingAction.RESPOND: return
        self.pending_action = PendingAction.WAIT
        if hand_index != -1 and (
            ((hand_index < len(self.hand) and self.hand[hand_index].name in self.expected_response)) or
            self.equipment[hand_index-len(self.hand)].name in self.expected_response):
            card = self.hand.pop(hand_index) if hand_index < len(self.hand) else self.equipment.pop(hand_index-len(self.hand))
            if isinstance(self.character, chd.MollyStark) and hand_index < len(self.hand)+1 and not self.is_my_turn and self.event_type != 'duel':
                self.hand.append(self.game.deck.draw())
            card.use_card(self)
            self.game.deck.scrap(card)
            self.notify_self()
            self.mancato_needed -= 1
            if self.mancato_needed <= 0:
                if self.event_type == 'duel':
                    self.game.duel(self, self.attacker.name)
                    if isinstance(self.character, chd.MollyStark) and hand_index < len(self.hand)+1 and not self.is_my_turn:
                        self.molly_discarded_cards += 1
                else:
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                self.event_type = ''
            else:
                self.pending_action = PendingAction.RESPOND
                self.notify_self()
        else:
            if isinstance(self.character, chd.MollyStark) and not self.is_my_turn:
                for i in range(self.molly_discarded_cards):
                    self.hand.append(self.game.deck.draw())
                self.molly_discarded_cards = 0
                self.notify_self()
            elif self.attacker and isinstance(self.attacker.character, chd.MollyStark) and self.is_my_turn:
                for i in range(self.attacker.molly_discarded_cards):
                    self.attacker.hand.append(self.attacker.game.deck.draw())
                self.attacker.molly_discarded_cards = 0
                self.attacker.notify_self()
            self.on_failed_response_cb()
            self.game.responders_did_respond_resume_turn(did_lose=True)
        if self.mancato_needed <= 0:
            self.attacker = None

    def get_sight(self, countWeapon=True):
        if not self.character:
            return 0
        aim = 0
        range = 0
        for card in self.equipment:
            if card.is_weapon and countWeapon:
                range += card.range
            else:
                aim += card.sight_mod
        if self.game.check_event(ce.Lazo):
            return 1 + self.character.sight_mod
        return max(1, range) + aim + self.character.sight_mod

    def get_visibility(self):
        if not self.character:
            return 0
        covers = 0
        for card in self.equipment:
            covers += card.vis_mod
        if self.game.check_event(ce.Lazo):
            return self.character.visibility_mod
        return self.character.visibility_mod + covers

    def scrap(self, card_index):
        if self.is_my_turn or isinstance(self.character, chars.SidKetchum):
            self.scrapped_cards += 1
            card = self.hand.pop(card_index)
            if isinstance(self.character, chars.SidKetchum) and self.scrapped_cards == 2:
                self.scrapped_cards = 0
                self.lives = min(self.lives+1, self.max_lives)
            elif isinstance(self.character, chd.JoseDelgrado) and card.is_equipment and self.special_use_count < 2:
                self.hand.append(self.game.deck.draw())
                self.hand.append(self.game.deck.draw())
                self.special_use_count += 1
            self.game.deck.scrap(card)
            self.notify_self()

    def holyday_special(self, data):
        if isinstance(self.character, chd.DocHolyday) and self.special_use_count < 1:
            self.special_use_count += 1
            cards = sorted(data['cards'], reverse=True)
            for c in cards:
                self.game.deck.scrap(self.hand.pop(c))
            self.notify_self()
            self.game.attack(self, data['against'])

    def chuck_lose_hp_draw(self):
        if isinstance(self.character, chd.ChuckWengam) and self.lives > 1 and self.is_my_turn:
            self.lives -= 1
            self.hand.append(self.game.deck.draw())
            self.hand.append(self.game.deck.draw())
            self.notify_self()

    def end_turn(self, forced=False):
        if not self.is_my_turn:
            return
        maxcards = self.lives if not isinstance(self.character, chd.SeanMallory) else 10
        if len(self.hand) > maxcards and not forced:
            print(
                f"I {self.name} have to many cards in my hand and I can't end the turn")
        elif self.pending_action == PendingAction.PLAY or forced:
            if not forced and self.game.check_event(ce.Vendetta):
                picked: cs.Card = self.game.deck.pick_and_scrap()
                self.sio.emit('chat_message', room=self.game.name, data=f'_flipped|{self.name}|{picked}')
                if picked.suit == cs.Suit.HEARTS:
                    self.play_turn()
                    return
            self.is_my_turn = False
            for i in range(len(self.equipment)):
                if self.equipment[i].usable_next_turn and not self.equipment[i].can_be_used_now:
                    self.equipment[i].can_be_used_now = True
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.next_turn()

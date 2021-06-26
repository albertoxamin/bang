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
        self.is_bot = bot
        self.game: g = None
        self.reset()

    def reset(self):
        self.hand: cs.Card = []
        self.equipment: cs.Card = []
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
        self.committed_suit_manette = None
        self.not_chosen_character = None
        try:
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
        self.gold_rush_equipment = []

    def join_game(self, game):
        self.game = game
        print(f'I {self.name} joined {self.game}')

    def disconnect(self):
        return self.game.handle_disconnect(self)

    def set_role(self, role: r.Role):
        self.role = role
        print(f'{self.name}: I am a {role.name}, my goal is "{role.goal}"')
        self.sio.emit('role', room=self.sid, data=json.dumps(
            role, default=lambda o: o.__dict__))

    def set_character(self, character: str):
        print(self.available_characters, character)
        if self.character == None:
            self.character = next(x for x in self.available_characters if x.name == character)
            if 'high_noon' in self.game.expansions:
                # questo viene utilizzato per la carta nuova identità
                self.not_chosen_character = next(x for x in self.available_characters if x.name != character)
            else:
                self.not_chosen_character = None
            self.real_character = self.character
            self.available_characters = []
            print(f'{self.name}: I chose character {self.character.name}')
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
        self.noStar = (self.game.initial_players == 3)

    def set_available_character(self, available):
        self.available_characters = available
        print(f'{self.name}: I have to choose between {available}')
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
            self.hand.append(self.game.deck.draw(True))
        if self.lives <= 0 and self.max_lives > 0 and not self.is_dead:
            print('dying, attacker', self.attacker)
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
        ser.pop('sio')
        ser.pop('sid')
        ser.pop('on_pick_cb')
        ser.pop('on_failed_response_cb')
        ser.pop('attacker')
        if self.attacker:
            ser['attacker'] = self.attacker.name
        ser['sight'] = self.get_sight()
        ser['lives'] = max(ser['lives'], 0)

        if self.lives <= 0 and self.max_lives > 0 and not self.is_dead:
            self.pending_action = PendingAction.WAIT
            ser['hand'] = []
            ser['equipment'] = []
            self.sio.emit('self', room=self.sid, data=json.dumps(
                ser, default=lambda o: o.__dict__))
            self.game.player_death(self)
        if self.game and self.game.started: # falso quando un bot viene eliminato dalla partita
            self.sio.emit('self_vis', room=self.sid, data=json.dumps(self.game.get_visible_players(self), default=lambda o: o.__dict__))
            self.game.notify_all()
        self.sio.emit('self', room=self.sid, data=json.dumps(
            ser, default=lambda o: o.__dict__))

    def bot_spin(self):
        while self.is_bot and self.game != None and not self.game.shutting_down:
            eventlet.sleep(max(0.2, uniform(self.game.bot_speed/2-0.1, self.game.bot_speed)))
            if self.lives > 0 or self.is_ghost:
                self.bot_logic()

    def bot_logic(self):
        if self.game == None or self.game.shutting_down: return
        if self.pending_action != None and self.pending_action != PendingAction.WAIT:
            # eventlet.sleep(uniform(self.game.bot_speed/2-0.1, self.game.bot_speed))
            pass
        else:
            return
        if self.pending_action == PendingAction.PICK:
            self.pick()
        elif self.pending_action == PendingAction.DRAW:
            self.draw('')
        elif self.pending_action == PendingAction.PLAY:
            non_blocked_cards = [card for card in self.hand if (not self.game.check_event(ceh.Manette) or card.suit == self.committed_suit_manette)]
            equippables = [c for c in non_blocked_cards if (c.is_equipment or c.usable_next_turn) and not isinstance(c, cs.Prigione) and not any([type(c) == type(x) for x in self.equipment])]
            misc = [c for c in non_blocked_cards if (isinstance(c, cs.WellsFargo) or isinstance(c, cs.Indiani) or isinstance(c, cs.Gatling) or isinstance(c, cs.Diligenza) or isinstance(c, cs.Emporio) or (isinstance(c, cs.Birra) and self.lives < self.max_lives and not self.game.check_event(ceh.IlReverendo)) or (c.need_with and len(self.hand) > 1 and not c.need_target and not (isinstance(c, csd.Whisky) and self.lives == self.max_lives)))
                    and not (not c.can_be_used_now and self.game.check_event(ce.IlGiudice))]
            need_target = [c for c in non_blocked_cards if c.need_target and c.can_be_used_now and not (c.need_with and len(self.hand) < 2) and not (
                (self.game.check_event(ceh.Sermone) or self.has_played_bang and not (any([isinstance(c, cs.Volcanic) for c in self.equipment]) and type(c) == type(cs.Bang)
            ) and not self.game.check_event(ce.Lazo))) and not ( isinstance(c, cs.Prigione) and self.game.check_event(ce.IlGiudice))]
            green_cards = [c for c in self.equipment if not self.game.check_event(ce.Lazo) and not isinstance(c, cs.Mancato) and c.usable_next_turn and c.can_be_used_now]
            if self.gold_nuggets > 0 and any([c.number <= self.gold_nuggets for c in self.game.deck.shop_cards]):
                for i in range(len(self.game.deck.shop_cards)):
                    if self.game.deck.shop_cards[i].number <= self.gold_nuggets:
                        self.buy_gold_rush_card(i)
                        return
            if len(equippables) > 0 and not self.game.check_event(ce.IlGiudice):
                for c in equippables:
                    if self.play_card(self.hand.index(c)):
                        return
            elif len(misc) > 0:
                for c in misc:
                    if c.need_with and self.play_card(self.hand.index(c), _with=sample([j for j in range(len(self.hand)) if j != self.hand.index(c)], 1)[0]):
                        return
                    elif self.play_card(self.hand.index(c)):
                        return
            elif len(need_target) > 0:
                for c in need_target:
                    _range = self.get_sight() if c.name == 'Bang!' or c.name == "Pepperbox" else c.range
                    others = [p for p in self.game.get_visible_players(self) if _range >= p['dist'] and not (isinstance(self.role, r.Vice) and p['is_sheriff']) and p['lives'] > 0 and not ((isinstance(c, cs.CatBalou) or isinstance(c, cs.Panico)) and p['cards'] == 0) and not (p['is_sheriff'] and isinstance(c, cs.Prigione))]
                    if len(others) == 0 or c not in self.hand:
                        continue
                    target = others[randrange(0, len(others))]
                    if target['is_sheriff'] and isinstance(self.role, r.Renegade):
                        target = others[randrange(0, len(others))]
                    if not c.need_with:
                        if self.play_card(self.hand.index(c), against=target['name']):
                            return
                    else:
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
            if maxcards == self.lives and len([c for c in self.gold_rush_equipment if isinstance(c, grc.Cinturone)]) > 0:
                maxcards = 8
            if len(self.hand) > maxcards:
                self.scrap(0)
            else:
                self.end_turn()
        elif self.pending_action == PendingAction.RESPOND:
            did_respond = False
            for i in range(len(self.hand)):
                if self.hand[i].can_be_used_now and (self.hand[i].name in self.expected_response or self.character.check(self.game, chd.ElenaFuente)):
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

    def play_turn(self, can_play_vendetta = True, again = False, can_play_again_don_bell=True):
        if (self.lives == 0 or self.is_dead) and not self.is_ghost:
            return self.end_turn(forced=True)
        self.scrapped_cards = 0
        self.can_play_ranch = True
        self.is_playing_ranch = False
        self.can_play_vendetta = can_play_vendetta
        self.can_play_again_don_bell = can_play_again_don_bell
        if not again:
            self.sio.emit('chat_message', room=self.game.name,
                          data=f'_turn|{self.name}')
            print(f'{self.name}: I was notified that it is my turn')
        self.was_shot = False
        self.is_my_turn = True
        self.is_waiting_for_action = True
        self.has_played_bang = False
        self.special_use_count = 0
        self.bang_used = 0
        if self.game.check_event(ceh.MezzogiornoDiFuoco):
            self.attacker = None
            self.lives -= 1
            if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Talismano)]) > 0:
                self.gold_nuggets += 1
            if self.character.check(self.game, grch.SimeonPicos):
                self.gold_nuggets += 1
            if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Stivali)]) > 0:
                self.hand.append(self.game.deck.draw())
            if self.character.check(self.game, chars.BartCassidy) and self.lives > 0:
                self.hand.append(self.game.deck.draw(True))
                self.sio.emit('chat_message', room=self.game.name, data=f'_special_bart_cassidy|{self.name}')
            self.heal_if_needed()
            if self.lives <= 0:
                return self.notify_self()

        #non è un elif perchè vera custer deve fare questo poi cambiare personaggio
        if self.game.check_event(ce.FratelliDiSangue) and self.lives > 1 and not self.is_giving_life and len([p for p in self.game.get_alive_players() if p != self and p.lives < p.max_lives]):
            self.available_cards = [{
                'name': p.name,
                'icon': p.role.icon if(self.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
                'alt_text': ''.join(['❤️']*p.lives)+''.join(['💀']*(p.max_lives-p.lives)),
                'noDesc': True
            } for p in self.game.get_alive_players() if p != self and p.lives < p.max_lives]
            self.available_cards.append({'icon': '❌', 'noDesc': True})
            self.choose_text = 'choose_fratelli_di_sangue'
            self.pending_action = PendingAction.CHOOSE
            self.is_giving_life = True
        elif self.game.check_event(ceh.NuovaIdentita) and self.not_chosen_character != None and not again:
            self.available_cards = [self.character, self.not_chosen_character]
            self.choose_text = 'choose_nuova_identita'
            self.pending_action = PendingAction.CHOOSE
        elif not self.game.check_event(ce.Lazo) and any([isinstance(c, cs.Dinamite) or isinstance(c, cs.Prigione) for c in self.equipment]):
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
        if self.is_my_turn and self.pending_action == PendingAction.PLAY and pile == 'event' and self.game.check_event(ce.Cecchino) and len([c for c in self.hand if c.name == cs.Bang(0,0).name]) >= 2:
            self.is_using_checchino = True
            self.available_cards = [{
                'name': p['name'],
                'icon': p['role'].icon if(self.game.initial_players == 3) else '⭐️' if p['is_sheriff'] else '🤠',
                'alt_text': ''.join(['❤️']*p['lives'])+''.join(['💀']*(p['max_lives']-p['lives'])),
                'desc': p['name']
            } for p in self.game.get_visible_players(self) if p['dist'] <= self.get_sight()]
            self.available_cards.append({'icon': '❌', 'noDesc': True})
            self.choose_text = 'choose_cecchino'
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        elif self.is_my_turn and self.pending_action == PendingAction.PLAY and pile == 'event' and self.game.check_event(ce.Rimbalzo) and len([c for c in self.hand if c.name == cs.Bang(0,0).name]) > 0:
            self.available_cards = [{
                'name': p.name,
                'icon': p.role.icon if(self.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
                'noDesc': True
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
        elif self.character.check(self.game, chars.KitCarlson):
            self.is_drawing = True
            self.available_cards = [self.game.deck.draw() for i in range(3)]
            self.choose_text = 'choose_card_to_get'
            self.pending_action = PendingAction.CHOOSE
            self.notify_self()
        elif self.character.check(self.game, grch.DutchWill):
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
            if pile == 'scrap' and self.character.check(self.game, chars.PedroRamirez):
                self.hand.append(self.game.deck.draw_from_scrap_pile())
                if not self.game.check_event(ceh.Sete):
                    self.hand.append(self.game.deck.draw())
                self.sio.emit('chat_message', room=self.game.name,
                              data=f'_draw_from_scrap|{self.name}')
            elif type(pile) == str and pile != self.name and pile in self.game.players_map and self.character.check(self.game, chars.JesseJones) and len(self.game.get_player_named(pile).hand) > 0:
                self.hand.append(self.game.get_player_named(pile).hand.pop(
                    randrange(0, len(self.game.get_player_named(pile).hand))))
                self.game.get_player_named(pile).notify_self()
                self.sio.emit('chat_message', room=self.game.name,
                              data=f'_draw_from_player|{self.name}|{pile}')
                if not self.game.check_event(ceh.Sete):
                    self.hand.append(self.game.deck.draw())
            elif self.character.check(self.game, chd.BillNoface):
                self.hand.append(self.game.deck.draw())
                if not self.game.check_event(ceh.Sete):
                    for i in range(self.max_lives-self.lives):
                        self.hand.append(self.game.deck.draw())
            else:
                if self.character.check(self.game, chd.PixiePete):
                    self.hand.append(self.game.deck.draw())
                for i in range(2):
                    card: cs.Card = self.game.deck.draw()
                    self.hand.append(card)
                    if i == 1 and (self.character.check(self.game, chars.BlackJack) or self.game.check_event(ce.LeggeDelWest)):
                        for p in self.game.get_alive_players():
                            if p != self:
                                p.notify_card(self, card, 'blackjack_special' if self.character.check(self.game, chars.BlackJack) else 'foc.leggedelwest')
                        if self.game.check_event(ce.LeggeDelWest):
                            card.must_be_used = True
                        if card.check_suit(self.game, [cs.Suit.HEARTS, cs.Suit.DIAMONDS]) and self.character.check(self.game, chars.BlackJack):
                            self.hand.append(self.game.deck.draw())
                    if self.game.check_event(ceh.Sete):
                        return self.notify_self()
                if self.game.check_event(ceh.IlTreno) or (self.is_ghost and self.game.check_event(ceh.CittaFantasma)):
                    self.hand.append(self.game.deck.draw())
                if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Piccone)]) > 0:
                    self.hand.append(self.game.deck.draw())
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
        if len([c for c in self.gold_rush_equipment if isinstance(c, grc.FerroDiCavallo)]) > 0:
            pickable_cards += 1
        if self.is_my_turn:
            for i in range(len(self.equipment)):
                if i < len(self.equipment) and isinstance(self.equipment[i], cs.Dinamite):
                    while pickable_cards > 0:
                        pickable_cards -= 1
                        picked: cs.Card = self.game.deck.pick_and_scrap()
                        print(f'Did pick {picked}')
                        self.sio.emit('chat_message', room=self.game.name,
                                      data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                        if picked.check_suit(self.game, [cs.Suit.SPADES]) and 2 <= picked.number <= 9 and pickable_cards == 0:
                            self.lives -= 3
                            if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Talismano)]) > 0:
                                self.gold_nuggets += 3
                            if self.character.check(self.game, grch.SimeonPicos):
                                self.gold_nuggets += 3
                            if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Stivali)]) > 0:
                                self.hand.append(self.game.deck.draw())
                                self.hand.append(self.game.deck.draw())
                                self.hand.append(self.game.deck.draw())
                            self.attacker = None
                            self.game.deck.scrap(self.equipment.pop(i), True)
                            self.sio.emit('chat_message', room=self.game.name, data=f'_explode|{self.name}')
                            self.heal_if_needed()
                            if self.character.check(self.game, chars.BartCassidy) and self.lives > 0:
                                for i in range(3):
                                    self.hand.append(self.game.deck.draw(True))
                                self.sio.emit('chat_message', room=self.game.name, data=f'_special_bart_cassidy|{self.name}')
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
                                      data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                        if not picked.check_suit(self.game, [cs.Suit.HEARTS]) and pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i), True)
                            self.sio.emit('chat_message', room=self.game.name, data=f'_prison_turn|{self.name}')
                            self.end_turn(forced=True)
                            return
                        elif pickable_cards == 0:
                            self.game.deck.scrap(self.equipment.pop(i), True)
                            self.sio.emit('chat_message', room=self.game.name, data=f'_prison_free|{self.name}')
                            break
                    break
            if any([isinstance(c, cs.Prigione) for c in self.equipment]):
                self.notify_self()
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
            if isinstance(card, cs.Bang) and self.has_played_bang and not any([isinstance(c, cs.Volcanic) for c in self.equipment]):
                continue
            elif isinstance(card, cs.Birra) and self.lives >= self.max_lives:
                continue
            else:
                playable_cards.append(i)
        return playable_cards

    def play_card(self, hand_index: int, against=None, _with=None):
        print(self.name, 'wants to play card ', hand_index, ' against:', against, ' with:', _with)
        if not self.is_my_turn or self.pending_action != PendingAction.PLAY or self.game.is_handling_death:
            print('but cannot')
            return
        if not (0 <= hand_index < len(self.hand) + len(self.equipment) + len(self.gold_rush_equipment)):
            print('but the card index is out of range')
            return
        elif len(self.hand) + len(self.equipment) <= hand_index < len(self.hand) + len(self.equipment) + len(self.gold_rush_equipment) and len(self.gold_rush_equipment):
            print('which is a gold rush black card')
            card: grc.ShopCard = self.gold_rush_equipment[hand_index - len(self.hand) + len(self.equipment)]
            return card.play_card(self)
        card: cs.Card = self.hand.pop(hand_index) if hand_index < len(self.hand) else self.equipment.pop(hand_index-len(self.hand))
        withCard: cs.Card = None
        if _with != None:
            withCard = self.hand.pop(_with) if hand_index > _with else self.hand.pop(_with - 1)
        print(self.name, 'is playing ', card, ' against:', against, ' with:', _with)
        did_play_card = False
        event_blocks_card = (self.game.check_event(ce.IlGiudice) and (card.is_equipment or (card.usable_next_turn and not card.can_be_used_now))) or (self.game.check_event(ce.Lazo) and card.usable_next_turn and card.can_be_used_now) or (self.game.check_event(ceh.Manette) and card.suit != self.committed_suit_manette and not (card.usable_next_turn and card.can_be_used_now))
        if not(against != None and (isinstance(self.game.get_player_named(against).character, chd.ApacheKid) or len([c for c in self.game.get_player_named(against).gold_rush_equipment if isinstance(c, grc.Calumet)]) > 0) and card.check_suit(self.game, [cs.Suit.DIAMONDS])) or (isinstance(card, grc.ShopCard) and card.kind == grc.ShopCardKind.BLACK) and not event_blocks_card:
            if against == self.name and not isinstance(card, csd.Tequila):
                did_play_card = False
            else:
                did_play_card = card.play_card(self, against, withCard)
        if not card.is_equipment and not card.usable_next_turn and not (isinstance(card, grc.ShopCard) and card.kind == grc.ShopCardKind.BLACK) or event_blocks_card:
            if did_play_card:
                self.game.deck.scrap(card, True)
            else:
                self.hand.insert(hand_index, card)
                if withCard:
                    self.hand.insert(_with, withCard)
        elif (card.usable_next_turn and card.can_be_used_now) or (isinstance(card, grc.ShopCard) and card.kind == grc.ShopCardKind.BLACK):
            if did_play_card:
                self.game.deck.scrap(card, True)
            else:
                self.equipment.insert(hand_index-len(self.hand), card)
        elif card.is_equipment or (card.usable_next_turn and not card.can_be_used_now):
            if not did_play_card:
                self.hand.insert(hand_index, card)
            else:
                did_play_card = True
        print("did play card:", did_play_card)
        self.notify_self()
        if self.is_bot:
            return did_play_card or card.is_equipment or (card.usable_next_turn and not card.can_be_used_now)

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
                card.reset_card()
                self.hand.append(card)
            else:
                self.game.deck.scrap(card, True)
            if self.event_type != 'rissa' or (self.event_type == 'rissa' and (len([p.name for p in self.game.get_alive_players() if p != self and (len(p.hand)+len(p.equipment)) > 0]) == 0 or self.target_p == [p.name for p in self.game.get_alive_players() if p != self and (len(p.hand)+len(p.equipment)) > 0][-1])):
                self.event_type = ''
                self.target_p = ''
                self.choose_action = ''
                self.pending_action = PendingAction.PLAY
            else:
                self.target_p = self.game.players[(self.game.players_map[self.target_p]+1)%len(self.game.players)].name
                while self.target_p == self.name or len(self.game.players[self.game.players_map[self.target_p]].hand) + len(self.game.players[self.game.players_map[self.target_p]].equipment) == 0:
                    self.target_p = self.game.players[(self.game.players_map[self.target_p]+1)%len(self.game.players)].name
            self.notify_self()
        elif self.choose_text == 'choose_ricercato':
            player = self.game.get_player_named(self.available_cards[card_index]['name'])
            player.sio.emit('chat_message', room=player.game.name, data=f'_play_card_against|{self.name}|Ricercato|{player.name}')
            if len([c for c in player.gold_rush_equipment if isinstance(c, grc.Ricercato)]) > 0:
                self.game.deck.shop_deck.append(grc.Ricercato())
            else:
                player.gold_rush_equipment.append(grc.Ricercato())
            player.notify_self()
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_sid_scrap':
            self.scrapped_cards += 1
            self.game.deck.scrap(self.hand.pop(card_index), True)
            if self.scrapped_cards == 2:
                self.available_cards = []
                self.pending_action = self.previous_pending_action
                if self.game.players[self.game.turn] != self:
                    self.game.players[self.game.turn].pending_action = PendingAction.PLAY
                    self.game.players[self.game.turn].notify_self()
            self.notify_self()
        elif self.choose_text == 'choose_bicchierino':
            player = self.game.get_player_named(self.available_cards[card_index]['name'])
            self.sio.emit('chat_message', room=self.game.name, data=f'_play_card_for|{self.name}|{"Bicchierino"}|{player.name}')
            player.lives = min(player.lives+1, player.max_lives)
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_birra_function':
            if card_index == 0:
                self.gold_nuggets += 1
            else:
                cs.Birra(1,1).play_card(self, skipChecks=True)
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_bottiglia':
            self.sio.emit('chat_message', room=self.game.name, data=f'_play_card|{self.name}|{"Bottiglia"}')
            if isinstance(self.available_cards[card_index], cs.Birra):
                self.lives = min(self.lives+1, self.max_lives)
            else:
                self.hand.append(self.available_cards[card_index])
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.choose_text == 'choose_complice':
            self.sio.emit('chat_message', room=self.game.name, data=f'_play_card|{self.name}|{"Bottiglia"}')
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
                self.sio.emit('chat_message', room=self.game.name, data=f'_gold_rush_pay_discard|{self.name}|{player.name}|{self.available_cards[card_index].name}')
                player.notify_self()
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.game.check_event(ceh.NuovaIdentita) and self.choose_text == 'choose_nuova_identita':
            if card_index == 1: # the other character
                self.character = self.not_chosen_character
                self.real_character = self.character
                self.max_lives = self.character.max_lives + self.role.health_mod
                self.lives = 2
                self.sio.emit('chat_message', room=self.game.name, data=f'_choose_character|{self.name}|{self.character.name}')
            self.play_turn(again = True)
        elif self.game.check_event(ceh.Manette) and self.choose_text == 'choose_manette':
            self.committed_suit_manette = cs.Suit(card_index)
            self.sio.emit('chat_message', room=self.game.name, data=f'_choose_manette|{self.name}|{"♦♣♥♠"[card_index]}')
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        elif self.is_giving_life and self.game.check_event(ce.FratelliDiSangue):
            try:
                player = self.game.get_player_named(self.available_cards[card_index]['name'])
                player.lives += 1
                self.lives -= 1
                if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Talismano)]) > 0:
                    self.gold_nuggets += 1
                if self.character.check(self.game, grch.SimeonPicos):
                    self.gold_nuggets += 1
                if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Stivali)]) > 0:
                    self.hand.append(self.game.deck.draw())
                player.notify_self()
                self.sio.emit('chat_message', room=self.game.name, data=f'_fratelli_sangue|{self.name}|{player.name}')
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
                    self.game.deck.scrap(self.discarded_cards[i], True)
                    self.hand.append(self.game.deck.draw())
                self.discarded_cards = []
                self.is_playing_ranch = False
                self.pending_action = PendingAction.PLAY
            else:
                self.discarded_cards.append(self.available_cards.pop(card_index))
            self.notify_self()
        elif self.game.dalton_on and self.game.check_event(ceh.IDalton):
            card = next(c for c in self.equipment if c == self.available_cards[card_index])
            self.equipment.remove(card)
            self.game.deck.scrap(card, True)
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.responders_did_respond_resume_turn()
        elif self.is_drawing and self.game.check_event(ce.Peyote):
            self.is_drawing = False
            card = self.game.deck.draw()
            self.sio.emit('chat_message', room=self.game.name, data=f"_guess|{self.name}|{self.available_cards[card_index]['icon']}")
            self.available_cards = []
            if card_index == card.suit%2:
                self.hand.append(card)
                self.sio.emit('chat_message', room=self.game.name, data=f"_guess_right|{self.name}")
                self.pending_action = PendingAction.DRAW
            else:
                self.game.deck.scrap(card)
                self.sio.emit('chat_message', room=self.game.name, data=f"_guess_wrong|{self.name}")
                self.pending_action = PendingAction.PLAY
            self.notify_self()
        # specifico per personaggio
        elif self.is_drawing and self.character.check(self.game, chars.KitCarlson):
            self.hand.append(self.available_cards.pop(card_index))
            pickable_stop = 1
            if self.game.check_event(ceh.Sete): pickable_stop = 2
            if self.game.check_event(ceh.IlTreno) or len([c for c in self.gold_rush_equipment if isinstance(c, grc.Piccone)]) > 0:
                pickable_stop = 0
            if len(self.available_cards) == pickable_stop:
                if len(self.available_cards) > 0:
                    self.game.deck.put_on_top(self.available_cards.pop())
                self.is_drawing = False
                self.pending_action = PendingAction.PLAY
                self.manette()
            self.notify_self()
        elif self.is_drawing and self.character.check(self.game, grch.DutchWill):
            self.hand.append(self.available_cards.pop(card_index))
            if self.game.check_event(ceh.IlTreno) or len([c for c in self.gold_rush_equipment if isinstance(c, grc.Piccone)]) > 0:
                self.hand.append(self.available_cards.pop(0))
            else:
                self.game.deck.scrap(self.available_cards.pop(0), True)
            self.gold_nuggets += 1
            self.is_drawing = False
            self.pending_action = PendingAction.PLAY
            self.notify_self()
        # specifico per personaggio
        elif self.is_drawing and self.character.check(self.game, chd.PatBrennan):
            self.is_drawing = False
            card = self.available_cards.pop(card_index)
            card.reset_card()
            self.hand.append(card)
            self.available_cards = []
            self.game.get_player_named(self.pat_target).notify_self()
            self.pending_action = PendingAction.PLAY
            self.manette()
            self.notify_self()
        else:  # emporio
            self.game.respond_emporio(self, card_index)

    def barrel_pick(self):
        pickable_cards = 1 + self.character.pick_mod
        if len([c for c in self.gold_rush_equipment if isinstance(c, grc.FerroDiCavallo)]) > 0:
            pickable_cards += 1
        if len([c for c in self.equipment if isinstance(c, cs.Barile)]) > 0 and self.character.check(self.game, chars.Jourdonnais):
            pickable_cards = 2
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cs.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            self.sio.emit('chat_message', room=self.game.name,
                            data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
            if picked.check_suit(self.game, [cs.Suit.HEARTS]):
                self.mancato_needed -= 1
                self.notify_self()
                if self.mancato_needed <= 0:
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                    return
        if not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Mancato) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente)]) == 0\
             and len([c for c in self.equipment if c.can_be_used_now and isinstance(c, cs.Mancato)]) == 0:
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
        if len([c for c in self.equipment if isinstance(c, cs.Barile)]) > 0 and self.character.check(self.game, chars.Jourdonnais):
            pickable_cards = 2
        if len([c for c in self.gold_rush_equipment if isinstance(c, grc.FerroDiCavallo)]) > 0:
            pickable_cards += 1
        while pickable_cards > 0:
            pickable_cards -= 1
            picked: cs.Card = self.game.deck.pick_and_scrap()
            print(f'Did pick {picked}')
            self.sio.emit('chat_message', room=self.game.name,
                            data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
            if picked.check_suit(self.game, [cs.Suit.HEARTS]):
                self.mancato_needed -= 1
                self.notify_self()
                if self.mancato_needed <= 0:
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                    return
        if not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Mancato) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente)]) == 0\
             and len([c for c in self.equipment if c.can_be_used_now and isinstance(c, cs.Mancato)]) == 0:
            self.take_no_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = self.game.deck.mancato_cards.copy()
            if self.character.check(self.game, chars.CalamityJanet) and cs.Bang(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Bang(0, 0).name)
            self.on_failed_response_cb = self.take_no_damage_response
            self.notify_self()

    def get_banged(self, attacker, double=False, no_dmg=False, card_index=None):
        self.attacker = attacker
        self.mancato_needed = 1 if not double else 2
        if card_index != None:
            self.dmg_card_index = card_index
        else:
            self.dmg_card_index = -1
        for i in range(len(self.equipment)):
            if self.equipment[i].can_be_used_now:
                print('usable', self.equipment[i])
        if not self.game.is_competitive and len([c for c in self.equipment if isinstance(c, cs.Barile)]) == 0 and not self.character.check(self.game, chars.Jourdonnais)\
             and len([c for c in self.hand if (isinstance(c, cs.Mancato) and c.can_be_used_now) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Bang)) or self.character.check(self.game, chd.ElenaFuente)]) == 0\
             and len([c for c in self.equipment if c.can_be_used_now and isinstance(c, cs.Mancato)]) == 0:
            print('Cant defend')
            if not no_dmg:
                self.take_damage_response()
            else:
                self.take_no_damage_response()
            return False
        else:
            if (not self.game.check_event(ce.Lazo) and len([c for c in self.equipment if isinstance(c, cs.Barile)]) > 0) and not self.game.players[self.game.turn].character.check(self.game, chd.BelleStar)\
                 or self.character.check(self.game, chars.Jourdonnais):
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
        if self.character.check(self.game, chd.ApacheKid) or len([c for c in self.gold_rush_equipment if isinstance(c, grc.Calumet)]) > 0: return False
        if not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Bang) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Mancato))]) == 0:
            print('Cant defend')
            self.take_damage_response()
            return False
        else:
            print('has bang')
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cs.Bang(0, 0).name]
            if self.character.check(self.game, chars.CalamityJanet) and cs.Mancato(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Mancato(0, 0).name)
            self.event_type = 'indians'
            self.on_failed_response_cb = self.take_damage_response
            return True

    def get_dueled(self, attacker):
        self.attacker = attacker
        if (self.game.check_event(ceh.Sermone) and self.is_my_turn) or (not self.game.is_competitive and len([c for c in self.hand if isinstance(c, cs.Bang) or (self.character.check(self.game, chars.CalamityJanet) and isinstance(c, cs.Mancato))]) == 0):
            print('Cant defend')
            self.take_damage_response()
            self.game.responders_did_respond_resume_turn(did_lose=True)
            return False
        else:
            self.pending_action = PendingAction.RESPOND
            self.expected_response = [cs.Bang(0, 0).name]
            if self.character.check(self.game, chars.CalamityJanet) and cs.Mancato(0, 0).name not in self.expected_response:
                self.expected_response.append(cs.Mancato(0, 0).name)
            self.event_type = 'duel'
            self.on_failed_response_cb = self.take_damage_response
            return True

    def heal_if_needed(self):
        while self.lives <= 0 and len(self.game.get_alive_players()) > 2 and len([c for c in self.hand if isinstance(c, cs.Birra)]) > 0 and not self.game.check_event(ceh.IlReverendo):
            for i in range(len(self.hand)):
                if isinstance(self.hand[i], cs.Birra):
                    if self.character.check(self.game, chd.MollyStark) and not self.is_my_turn:
                        self.hand.append(self.game.deck.draw(True))
                    self.lives += 1 if not self.character.check(self.game, chd.TequilaJoe) else 2
                    self.lives = min(self.lives, self.max_lives)
                    self.game.deck.scrap(self.hand.pop(i), True)
                    self.sio.emit('chat_message', room=self.game.name,
                                  data=f'_beer_save|{self.name}')
                    break

    def take_damage_response(self):
        self.lives -= 1
        if self.lives > 0:
            if self.character.check(self.game, chars.BartCassidy):
                self.sio.emit('chat_message', room=self.game.name,
                                data=f'_special_bart_cassidy|{self.name}')
                self.hand.append(self.game.deck.draw(True))
            elif self.character.check(self.game, chars.ElGringo) and self.attacker and self.attacker in self.game.get_alive_players() and len(self.attacker.hand) > 0:
                self.hand.append(self.attacker.hand.pop(randrange(0, len(self.attacker.hand))))
                self.hand[-1].reset_card()
                self.sio.emit('chat_message', room=self.game.name,
                              data=f'_special_el_gringo|{self.name}|{self.attacker.name}')
                self.attacker.notify_self()
        if self.attacker and 'gold_rush' in self.game.expansions:
            self.attacker.gold_nuggets += 1
            self.attacker.notify_self()
            if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Talismano)]) > 0:
                self.gold_nuggets += 1
            if self.character.check(self.game, grch.SimeonPicos):
                self.gold_nuggets += 1
            if len([c for c in self.gold_rush_equipment if isinstance(c, grc.Stivali)]) > 0:
                self.hand.append(self.game.deck.draw())
        self.heal_if_needed()
        self.mancato_needed = 0
        self.expected_response = []
        self.event_type = ''
        self.notify_self()
        self.attacker = None

    def take_no_damage_response(self):
        if self.dmg_card_index != None and self.dmg_card_index != -1 and self.game.check_event(ce.Rimbalzo):
            self.game.deck.scrap(self.equipment.pop(self.dmg_card_index))
        self.dmg_card_index = -1
        self.mancato_needed = 0
        self.expected_response = []
        self.event_type = ''
        self.notify_self()
        self.attacker = None

    def respond(self, hand_index):
        if self.pending_action != PendingAction.RESPOND: return
        self.pending_action = PendingAction.WAIT
        if hand_index != -1 and hand_index < (len(self.hand)+len(self.equipment)) and (
            ((hand_index < len(self.hand) and self.hand[hand_index].name in self.expected_response) or self.character.check(self.game, chd.ElenaFuente)) or
            (hand_index-len(self.hand) < len(self.equipment) and self.equipment[hand_index-len(self.hand)].name in self.expected_response)):
            card = self.hand.pop(hand_index) if hand_index < len(self.hand) else self.equipment.pop(hand_index-len(self.hand))
            #hand_index < len(self.hand) with the '<=' due to the hand.pop
            if self.character.check(self.game, chd.MollyStark) and hand_index <= len(self.hand) and not self.is_my_turn and self.event_type != 'duel':
                if self.attacker.character.check(self.game, chars.SlabTheKiller) and isinstance(self.hand[hand_index], cs.Mancato):
                    self.molly_discarded_cards += 1
                else:
                    self.hand.append(self.game.deck.draw(True))
            card.use_card(self)
            self.sio.emit('chat_message', room=self.game.name, data=f'_respond|{self.name}|{card.name}')
            self.game.deck.scrap(card, True)
            self.notify_self()
            self.mancato_needed -= 1
            if self.mancato_needed <= 0:
                if self.event_type == 'duel':
                    self.game.duel(self, self.attacker.name)
                    if self.character.check(self.game, chd.MollyStark) and hand_index < len(self.hand) and not self.is_my_turn:
                        self.molly_discarded_cards += 1
                else:
                    if self.character.check(self.game, chd.MollyStark) and not self.is_my_turn:
                        for i in range(self.molly_discarded_cards):
                            self.hand.append(self.game.deck.draw(True))
                        self.molly_discarded_cards = 0
                        self.notify_self()
                    self.game.responders_did_respond_resume_turn(did_lose=False)
                self.event_type = ''
            else:
                self.pending_action = PendingAction.RESPOND
                self.notify_self()
        else:
            if self.character.check(self.game, chd.MollyStark) and not self.is_my_turn:
                for i in range(self.molly_discarded_cards):
                    self.hand.append(self.game.deck.draw(True))
                self.molly_discarded_cards = 0
                self.notify_self()
            elif self.attacker and self.attacker in self.game.get_alive_players() and self.attacker.character.check(self.game, chd.MollyStark) and self.is_my_turn:
                for i in range(self.attacker.molly_discarded_cards):
                    self.attacker.hand.append(self.attacker.game.deck.draw(True))
                self.attacker.molly_discarded_cards = 0
                self.attacker.notify_self()
            self.on_failed_response_cb()
            if self.game:
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
        if not self.character or not self.game or not self.game.players[self.game.turn].character:
            return 0
        covers = 0
        if self.game.check_event(ce.Lazo) or self.game.players[self.game.turn].character.check(self.game, chd.BelleStar):
            return self.character.visibility_mod
        for card in self.equipment:
            covers += card.vis_mod
        return self.character.visibility_mod + covers

    def scrap(self, card_index):
        if self.is_my_turn or self.character.check(self.game, chars.SidKetchum):
            self.scrapped_cards += 1
            card = self.hand.pop(card_index)
            if self.character.check(self.game, chars.SidKetchum) and self.scrapped_cards == 2:
                self.scrapped_cards = 0
                self.lives = min(self.lives+1, self.max_lives)
            elif self.character.check(self.game, chd.JoseDelgado) and card.is_equipment and self.special_use_count < 2:
                self.hand.append(self.game.deck.draw(True))
                self.hand.append(self.game.deck.draw(True))
                self.special_use_count += 1
            self.game.deck.scrap(card)
            self.notify_self()

    def special(self, data):
        self.character.special(self, data)

    def gold_rush_discard(self):
        self.available_cards = [{
            'name': p.name,
            'icon': p.role.icon if(self.game.initial_players == 3) else '⭐️' if isinstance(p.role, r.Sheriff) else '🤠',
            'alt_text': ''.join(['🎴️'] * len(p.gold_rush_equipment)),
            'noDesc': True
        } for p in self.game.get_alive_players() if p != self and len([e for e in p.gold_rush_equipment if e.number <= self.gold_nuggets + 1]) > 0]
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

    def end_turn(self, forced=False):
        print(f"{self.name} wants to end his turn")
        if not self.is_my_turn and not forced:
            return
        maxcards = self.lives if not self.character.check(self.game, chd.SeanMallory) else 10
        if maxcards == self.lives and len([c for c in self.gold_rush_equipment if isinstance(c, grc.Cinturone)]) > 0:
            maxcards = 8
        if len(self.hand) > maxcards and not forced:
            print(
                f"{self.name}: I have to many cards in my hand and I can't end the turn")
        elif self.pending_action == PendingAction.PLAY or forced:
            if not forced and self.game.check_event(ce.Vendetta) and self.can_play_vendetta:
                picked: cs.Card = self.game.deck.pick_and_scrap()
                self.sio.emit('chat_message', room=self.game.name, data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                if picked.check_suit(self.game, [cs.Suit.HEARTS]):
                    self.play_turn(can_play_vendetta=False)
                    return
            if not forced and self.character.check(self.game, grch.DonBell) and self.can_play_again_don_bell:
                picked: cs.Card = self.game.deck.pick_and_scrap()
                self.sio.emit('chat_message', room=self.game.name, data=f'_flipped|{self.name}|{picked.name}|{picked.num_suit()}')
                if picked.check_suit(self.game, [cs.Suit.HEARTS, cs.Suit.DIAMONDS]):
                    self.play_turn(can_play_vendetta=False, can_play_again_don_bell=False)
                    return
            self.is_my_turn = False
            self.has_played_bang = False
            for i in range(len(self.equipment)):
                if self.equipment[i].usable_next_turn and not self.equipment[i].can_be_used_now:
                    self.equipment[i].can_be_used_now = True
            for i in range(len(self.hand)):
                if self.hand[i].must_be_used:
                    self.hand[i].must_be_used = False
            if self.is_dead and self.is_ghost and self.game.check_event(ceh.CittaFantasma):
                self.is_ghost = False
                for i in range(len(self.hand)):
                    self.game.deck.scrap(self.hand.pop(), True)
                for i in range(len(self.equipment)):
                    self.game.deck.scrap(self.equipment.pop(), True)
            self.committed_suit_manette = None
            self.pending_action = PendingAction.WAIT
            self.notify_self()
            self.game.next_turn()

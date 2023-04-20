import json
from typing import List, Set, Dict, Tuple, Optional
import random
import socketio
import eventlet

import bang.players as pl
import bang.cards as cs
import bang.characters as characters
import bang.expansions.dodge_city.characters as chd
import bang.expansions.wild_west_show.characters as chwws
from bang.deck import Deck
import bang.roles as roles
import bang.expansions.fistful_of_cards.card_events as ce
import bang.expansions.high_noon.card_events as ceh
import bang.expansions.wild_west_show.card_events as cew
import bang.expansions.gold_rush.shop_cards as grc
import bang.expansions.gold_rush.characters as grch
import bang.expansions.the_valley_of_shadows.cards as tvosc
from metrics import Metrics
from globals import G


debug_commands = [
    {"cmd": "/debug", "help": "Toggles the debug mode"},
    {
        "cmd": "/set_chars",
        "help": "Set how many characters to distribute - sample /set_chars 3",
    },
    {"cmd": "/suicide", "help": "Kills you"},
    {"cmd": "/nextevent", "help": "Flip the next event card"},
    {
        "cmd": "/notify",
        "help": "Send a message to a player - sample /notify player hi!",
    },
    {
        "cmd": "/show_cards",
        "help": "View the hand of another - sample /show_cards player",
    },
    {"cmd": "/ddc", "help": "Destroy all cards - sample /ddc player"},
    {"cmd": "/dsh", "help": "Set health - sample /dsh player"},
    # {'cmd':'/togglebot', 'help':''},
    {"cmd": "/cancelgame", "help": "Stops the current game"},
    {"cmd": "/startgame", "help": "Force starts the game"},
    {
        "cmd": "/setbotspeed",
        "help": "Changes the bot response time - sample /setbotspeed 0.5",
    },
    # {'cmd':'/addex', 'help':''},
    {
        "cmd": "/setcharacter",
        "help": "Changes your current character - sample /setcharacter Willy The Kid",
    },
    {"cmd": "/setevent", "help": "Changes the event deck - sample /setevent 0 Manette"},
    {
        "cmd": "/removecard",
        "help": "Remove a card from hand/equip - sample /removecard 0",
    },
    {"cmd": "/getcard", "help": "Get a brand new card - sample /getcard Birra"},
    {"cmd": "/meinfo", "help": "Get player data"},
    {"cmd": "/gameinfo", "help": "Get game data"},
    {"cmd": "/deckinfo", "help": "Get deck data"},
    {"cmd": "/trainfw", "help": "move train forward"},
    {"cmd": "/playerinfo", "help": "Get player data - sample /playerinfo player"},
    {"cmd": "/cardinfo", "help": "Get card data - sample /cardinfo handindex"},
    {"cmd": "/mebot", "help": "Toggles bot mode"},
    {"cmd": "/getnuggets", "help": "Adds nuggets to yourself - sample /getnuggets 5"},
    {"cmd": "/startwithseed", "help": "start the game with custom seed"},
    {
        "cmd": "/getset",
        "help": "get extension set of cards sample - /get valley",
        "admin": True,
    },
]


class Game:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.players: List[pl.Player] = []
        self.spectators: List[pl.Player] = []
        self.deck: Deck = None
        self.started = False
        self.turn = 0
        self.ready_count = 0
        self.waiting_for = 0
        self.initial_players = 0
        self.password = ""
        self.expansions: List[str] = []
        self.available_expansions = [
            "dodge_city",
            "fistful_of_cards",
            "high_noon",
            "gold_rush",
            "the_valley_of_shadows",
            "wild_west_show",
            "train_robbery",
        ]
        self.shutting_down = False
        self.is_competitive = False
        self.disconnect_bot = True
        self.player_bangs = 0
        self.is_russian_roulette_on = False
        self.dalton_on = False
        self.poker_on = False
        self.bot_speed = 1.5
        self.incremental_turn = 0
        self.did_resuscitate_deadman = False
        self.is_handling_death = False
        self.pending_winners: List[pl.Player] = []
        self.someone_won = False
        self.attack_in_progress = False
        self.characters_to_distribute = 2  # personaggi da dare a inizio partita
        self.debug = self.name == "debug"
        self.dead_roles: List[roles.Role] = []
        self.is_changing_pwd = False
        self.is_hidden = False
        self.rng = random.Random()
        self.rpc_log = []
        self.is_replay = False
        self.replay_speed = 1

    def shuffle_players(self):
        if not self.started:
            random.shuffle(self.players)
            self.notify_room()

    def reset(self):
        for p in self.players:
            if p.sid == p.name:
                p.is_bot = True
        if self.is_replay:
            self.is_replay = False
            print("replay ended")
        print(f"{self.name}: resetting lobby")
        self.players.extend(self.spectators)
        self.spectators = []
        for bot in [p for p in self.players if p.is_bot]:
            if bot.was_player:
                bot.is_bot = False
            else:
                bot.game = None
        self.players = [p for p in self.players if not p.is_bot and p.sid != "a_replay"]
        print(f"{self.name}: players: {self.players}")
        self.started = False
        self.is_handling_death = False
        self.waiting_for = 0
        self.incremental_turn = 0
        self.turn = 0
        self.pending_winners = []
        self.dead_roles: List[roles.Role] = []
        for p in self.players:
            p.reset()
            p.notify_self()
        eventlet.sleep(0.5)
        self.notify_room()

    def replay(self, log, speed=1.0, fast_forward=-1):
        self.players = []
        self.is_hidden = True
        self.is_replay = True
        self.replay_speed = speed
        for i in range(len(log) - 1):
            print("replay:", i, "of", len(log) - 3, "->", log[i])
            if len(self.spectators) == 0:
                break
            if log[i] == "@@@":
                eventlet.sleep(10)
                if self.is_replay:
                    self.reset()
                return
            cmd = log[i].split(";")
            if cmd[1] == "players":
                self.expansions = json.loads(cmd[4].replace("'", '"'))
                self.is_competitive = bool(cmd[5])
                pnames = json.loads(cmd[3].replace("'", '"'))
                for p in pnames:
                    self.add_player(pl.Player(p, "a_replay", bot=False))
                continue
            if cmd[1] == "start_game":
                self.start_game(int(cmd[2]))
                continue
            player = [p for p in self.players if p.name == cmd[0]][0]
            if cmd[1] == "set_character":
                if player.character is not None and isinstance(
                    player.real_character, chd.VeraCuster
                ):
                    player.set_available_character(
                        [p.character for p in self.get_alive_players() if p != player]
                    )
                player.set_character(cmd[2])
            if cmd[1] == "draw":
                player.draw(cmd[2])
            if cmd[1] == "pick":
                player.pick()
            if cmd[1] == "end_turn":
                player.end_turn()
            if cmd[1] == "play_card":
                data = json.loads(cmd[2])
                if len(data) != 0:
                    player.play_card(data["index"], data["against"], data["with"])
                else:
                    player.special(
                        data
                    )  # TODO: remove this, is only for the typo in the log
            if cmd[1] == "respond":
                player.respond(int(cmd[2]))
            if cmd[1] == "choose":
                player.choose(int(cmd[2]))
            if cmd[1] == "scrap":
                player.scrap(int(cmd[2]))
            if cmd[1] == "special":
                player.special(json.loads(cmd[2]))
            if cmd[1] == "gold_rush_discard":
                player.gold_rush_discard()
            if cmd[1] == "buy_gold_rush_card":
                player.buy_gold_rush_card(int(cmd[2]))
            # if cmd[1] == 'chat_message':
            #     chat_message(None, cmd[2], player)
            if i == fast_forward:
                self.replay_speed = 1.0
            self.notify_room()
            eventlet.sleep(max(self.replay_speed, 0.001))
        eventlet.sleep(6)
        self.players = []
        if self.is_replay:
            self.reset()

    def notify_room(self, sid=None):
        """Notify all players in the room of the room's state."""
        if any((p.character is None for p in self.players)) or sid:
            G.sio.emit(
                "room",
                room=self.name if not sid else sid,
                data={
                    "name": self.name,
                    "started": self.started,
                    "players": [
                        {
                            "name": p.name,
                            "ready": p.character is not None,
                            "is_bot": p.is_bot,
                            "avatar": p.avatar,
                        }
                        for p in self.players
                    ],
                    "password": self.password,
                    "is_competitive": self.is_competitive,
                    "disconnect_bot": self.disconnect_bot,
                    "expansions": self.expansions,
                    "available_expansions": self.available_expansions,
                    "is_replay": self.is_replay,
                    "characters_to_distribute": self.characters_to_distribute,
                },
            )
        G.sio.emit("debug", room=self.name, data=self.debug)
        if self.debug:
            G.sio.emit(
                "commands",
                room=self.name,
                data=[x for x in debug_commands if "admin" not in x],
            )
        else:
            G.sio.emit(
                "commands",
                room=self.name,
                data=[{"cmd": "/debug", "help": "Toggles the debug mode"}],
            )
        G.sio.emit("spectators", room=self.name, data=len(self.spectators))

    def toggle_expansion(self, expansion_name):
        """Toggles an expansion on or off."""
        if not self.started:
            print(f"{self.name}: toggling", expansion_name)
            if expansion_name in self.expansions:
                self.expansions.remove(expansion_name)
            else:
                self.expansions.append(expansion_name)
            self.notify_room()

    def toggle_competitive(self):
        """Toggles the competitive mode on or off."""
        self.is_competitive = not self.is_competitive
        self.notify_room()

    def toggle_disconnect_bot(self):
        """Toggles the disconnect bot on or off."""
        self.disconnect_bot = not self.disconnect_bot
        self.notify_room()

    def feature_flags(self):
        if (
            "the_valley_of_shadows" not in self.expansions
            and "the_valley_of_shadows" not in self.available_expansions
        ):
            self.available_expansions.append("the_valley_of_shadows")
        self.notify_room()

    def add_player(self, player: pl.Player):
        if player.is_bot and len(self.players) >= 8:
            return
        if player in self.players or len(self.players) >= 10:
            return
        player.join_game(self)
        if player.is_admin():
            self.feature_flags()
        self.players.append(player)
        if len(self.players) > 7:
            if "dodge_city" not in self.expansions:
                self.expansions.append("dodge_city")
        print(f"{self.name}: Added player {player.name} to game; {len(self.players)=}")
        self.notify_room()
        G.sio.emit("chat_message", room=self.name, data=f"_joined|{player.name}")

    def set_private(self):
        if not self.is_changing_pwd:
            self.is_changing_pwd = True
            if self.password == "":
                self.password = "".join(
                    random.choice("AEOUJKZT123456789") for x in range(6)
                )
                print(self.name, "is now private pwd", self.password)
            else:
                self.password = ""
            self.notify_room()
            eventlet.sleep(0.2)
            self.is_changing_pwd = False

    def notify_character_selection(self):
        self.notify_room()
        if not any((p.character is None for p in self.players)):
            for i, player in enumerate(self.players):
                print(self.name, player.name, player.character)
                if player.is_bot and "AI" in player.name:
                    player.name = f"{player.character.name} AI"
                G.sio.emit(
                    "chat_message",
                    room=self.name,
                    data=f"_choose_character|{player.name}|{player.character.name}",
                )
                player.prepare()
                cards_to_draw = (
                    player.max_lives
                    if not player.character.check(self, chwws.BigSpencer)
                    else 5
                )
                for _ in range(cards_to_draw):
                    self.deck.draw(player=player)
                player.notify_self()
            self.players_map = {c.name: i for i, c in enumerate(self.players)}
            current_roles = [p.role.name for p in self.players]
            self.rng.shuffle(current_roles)
            roles_str = ""
            for role in current_roles:
                if role not in roles_str:
                    roles_str += f"|{role}|{str(current_roles.count(role))}"
            G.sio.emit("chat_message", room=self.name, data=f"_allroles{roles_str}")
            self.play_turn()
            self.notify_stations()

    def choose_characters(self):
        n = self.characters_to_distribute
        all_chars = characters.all_characters(self.expansions)
        if len(all_chars) // len(self.players) < n:
            n = len(all_chars) // len(self.players)
        char_cards = self.rng.sample(all_chars, len(self.players) * n)
        for i, player in enumerate(self.players):
            player.set_available_character(char_cards[i * n : i * n + n])

    def start_game(self, SEED=None):
        if self.started:
            return
        print(f"{self.name}: GAME IS STARING")
        if SEED is None:
            import time  # pylint: disable=import-outside-toplevel

            SEED = int(time.time())
        print(f"{self.name}: SEED IS {SEED}")
        self.SEED = SEED  # pylint: disable=invalid-name
        self.rpc_log = [
            f";players;{len(self.players)};{[p.name for p in self.players]};{self.expansions};{self.is_competitive}",
            f";start_game;{SEED}",
        ]
        self.rng = random.Random(SEED)
        self.players_map = {c.name: i for i, c in enumerate(self.players)}
        G.sio.emit("chat_message", room=self.name, data="_starting")
        G.sio.emit("start", room=self.name)
        self.started = True
        self.someone_won = False
        self.attack_in_progress = False
        self.attack_queue = []
        self.deck = Deck(self)
        self.initial_players = len(self.players)
        self.distribute_roles()
        self.choose_characters()
        if "gold_rush" in self.expansions:
            self.notify_gold_rush_shop()
        if not self.is_replay:
            Metrics.send_metric(
                "start_game",
                points=[1],
                tags=(
                    [f"exp:{e}" for e in self.expansions]
                    + [
                        f"players:{self.initial_players}",
                        f"competitive:{self.is_competitive}",
                    ]
                ),
            )

    def distribute_roles(self):
        available_roles: List[roles.Role] = []
        if len(self.players) == 3:
            available_roles = [
                roles.Vice(
                    "Elimina il Rinnegato 🦅, se non lo elimini tu elimina anche il Fuorilegge",
                    "Kill the Renegade 🦅, if you are not the one who kills him then kill the Outlaw!",
                ),
                roles.Renegade(
                    "Elimina il Fuorilegge 🐺, se non lo elimini tu elimina anche il Vice",
                    "Kill the Outlaw 🐺, if you are not the one who kills him then kill the Vice!",
                ),
                roles.Outlaw(
                    "Elimina il Vice 🎖, se non lo elimini tu elimina anche il Rinnegato",
                    "Kill the Vice 🎖, if you are not the one who kills him then kill the Renegade!",
                ),
            ]
        elif len(self.players) >= 4:
            available_roles = [
                roles.Sheriff(),
                roles.Renegade(),
                roles.Outlaw(),
                roles.Outlaw(),
                roles.Vice(),
                roles.Outlaw(),
                roles.Vice(),
                roles.Renegade(),
                roles.Outlaw(),
                roles.Vice(),
                roles.Outlaw(),
            ]
            available_roles = available_roles[: len(self.players)]
        else:
            available_roles = [roles.Renegade(), roles.Renegade()]
        self.rng.shuffle(available_roles)
        for i, player in enumerate(self.players):
            player.set_role(available_roles[i])
            if isinstance(available_roles[i], roles.Sheriff) or (
                len(available_roles) == 3 and isinstance(available_roles[i], roles.Vice)
            ):
                if isinstance(available_roles[i], roles.Sheriff):
                    G.sio.emit(
                        "chat_message",
                        room=self.name,
                        data=f"_sheriff|{player.name}",
                    )
                self.turn = i
            player.notify_self()
        self.notify_event_card()
        if "wild_west_show" in self.expansions:
            self.notify_event_card_wildwestshow()

    def discard_others(self, attacker: pl.Player, card_name: str = None):
        self.attack_in_progress = True
        attacker.pending_action = pl.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.ready_count = 0
        for p in self.get_alive_players():
            if len(p.hand) > 0 and (p != attacker or card_name == "Tornado"):
                if p.get_discarded(attacker=attacker, card_name=card_name):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = pl.PendingAction.PLAY
            attacker.notify_self()
            self.attack_in_progress = False
        elif card_name == "Poker":
            self.poker_on = True

    def attack_others(self, attacker: pl.Player, card_name: str = None):
        self.attack_in_progress = True
        attacker.pending_action = pl.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.ready_count = 0
        for p in self.get_alive_players():
            if p != attacker:
                if p.get_banged(attacker=attacker, card_name=card_name):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = pl.PendingAction.PLAY
            attacker.notify_self()
            self.attack_in_progress = False
        if self.pending_winners and not self.someone_won:
            return self.announces_winners()

    def indian_others(self, attacker: pl.Player):
        self.attack_in_progress = True
        attacker.pending_action = pl.PendingAction.WAIT
        attacker.notify_self()
        self.waiting_for = 0
        self.ready_count = 0
        for p in self.get_alive_players():
            if p != attacker:
                if p.get_indians(attacker=attacker):
                    self.waiting_for += 1
                    p.notify_self()
        if self.waiting_for == 0:
            attacker.pending_action = pl.PendingAction.PLAY
            attacker.notify_self()
            self.attack_in_progress = False
        if self.pending_winners and not self.someone_won:
            return self.announces_winners()

    def can_card_reach(self, card: cs.Card, player: pl.Player, target: str):
        if card and card.range != 0 and card.range < 99:
            return not any(
                (
                    True
                    for p in self.get_visible_players(player)
                    if p["name"] == target and p["dist"] > card.range
                )
            )
        return True

    def attack(
        self,
        attacker: pl.Player,
        target_username: str,
        double: bool = False,
        card_name: str = None,
        skip_queue: bool = False,
    ):
        if self.attack_in_progress and not skip_queue:
            self.attack_queue.append((attacker, target_username, double, card_name))
            print(
                f"attack in progress, queueing the attack queue len:{len(self.attack_queue)}"
            )
            return
        if self.get_player_named(target_username).get_banged(
            attacker=attacker, double=double, card_name=card_name
        ):
            self.attack_in_progress = True
            self.ready_count = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()
        elif not attacker.is_my_turn or len(self.attack_queue) == 0:
            self.players[self.turn].pending_action = pl.PendingAction.PLAY

    def steal_discard(self, attacker: pl.Player, target_username: str, card: cs.Card):
        p = self.get_player_named(target_username)
        if p != attacker and p.get_discarded(
            attacker,
            card_name=card.name,
            action="steal" if isinstance(card, cs.Panico) else "discard",
        ):
            self.ready_count = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()
        else:
            attacker.pending_action = pl.PendingAction.CHOOSE
            attacker.target_p = target_username
            if isinstance(card, cs.CatBalou):
                attacker.choose_action = "discard"
            elif isinstance(card, cs.Panico):
                attacker.choose_action = "steal"
            attacker.notify_self()

    def rimbalzo(self, attacker: pl.Player, target_username: str, card_index: int):
        if self.get_player_named(target_username).get_banged(
            attacker=attacker, no_dmg=True, card_index=card_index
        ):
            self.ready_count = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def duel(self, attacker: pl.Player, target_username: str):
        if self.get_player_named(target_username).get_dueled(attacker=attacker):
            self.ready_count = 0
            self.waiting_for = 1
            attacker.pending_action = pl.PendingAction.WAIT
            attacker.notify_self()
            self.get_player_named(target_username).notify_self()

    def emporio(self):
        pls = self.get_alive_players()
        self.available_cards = [self.deck.draw(True) for i in range(len(pls))]
        self.players[self.turn].pending_action = pl.PendingAction.CHOOSE
        self.players[self.turn].choose_text = "choose_card_to_get"
        self.players[self.turn].available_cards = self.available_cards
        G.sio.emit(
            "emporio",
            room=self.name,
            data=json.dumps(
                {"name": self.players[self.turn].name, "cards": self.available_cards},
                default=lambda o: o.__dict__,
            ),
        )
        self.players[self.turn].notify_self()

    def respond_emporio(self, player: pl.Player, i: int):
        card = self.available_cards.pop(i)
        G.sio.emit(
            "chat_message",
            room=self.name,
            data=f"_choose_emporio|{player.name}|{card.name}",
        )
        player.hand.append(card)
        player.available_cards = []
        player.pending_action = pl.PendingAction.WAIT
        player.notify_self()
        pls = self.get_alive_players()
        next_player = pls[
            (
                pls.index(self.players[self.turn])
                + (len(pls) - len(self.available_cards))
            )
            % len(pls)
        ]
        if len(self.available_cards) == 1:
            G.sio.emit(
                "chat_message",
                room=self.name,
                data=f"_choose_emporio|{next_player.name}|{self.available_cards[0].name}",
            )
            next_player.hand.append(self.available_cards.pop())
            next_player.notify_self()
            G.sio.emit("emporio", room=self.name, data='{"name":"","cards":[]}')
            self.players[self.turn].pending_action = pl.PendingAction.PLAY
            self.players[self.turn].notify_self()
        elif next_player == self.players[self.turn]:
            G.sio.emit("emporio", room=self.name, data='{"name":"","cards":[]}')
            self.players[self.turn].pending_action = pl.PendingAction.PLAY
            self.players[self.turn].notify_self()
        else:
            next_player.pending_action = pl.PendingAction.CHOOSE
            next_player.choose_text = "choose_card_to_get"
            next_player.available_cards = self.available_cards
            G.sio.emit(
                "emporio",
                room=self.name,
                data=json.dumps(
                    {"name": next_player.name, "cards": self.available_cards},
                    default=lambda o: o.__dict__,
                ),
            )
            next_player.notify_self()

    def get_player_named(self, name: str, next=False) -> pl.Player:
        if next:
            return self.players[(self.players_map[name] + 1) % len(self.players)]
        return self.players[self.players_map[name]]

    def responders_did_respond_resume_turn(self, did_lose=False):
        """Called when all Players have responded to an event/attack."""
        print(f"{self.name}: did_lose", did_lose)
        if self.player_bangs > 0 and self.check_event(ce.PerUnPugnoDiCarte):
            self.player_bangs -= 1
            if self.player_bangs >= 1:
                print(f"{self.name}: bang again")
                if self.players[self.turn].get_banged(self.deck.event_cards[0]):
                    self.players[self.turn].notify_self()
                else:
                    self.responders_did_respond_resume_turn()
            else:
                print(f"{self.name}: ok play turn now")
                self.player_bangs = 0
                self.players[self.turn].play_turn()
        elif self.is_russian_roulette_on and self.check_event(ce.RouletteRussa):
            pls = self.get_alive_players()
            if did_lose:
                target_pl = pls[
                    (pls.index(self.players[self.turn]) + self.player_bangs) % len(pls)
                ]
                print(f"{self.name}: stop roulette")
                target_pl.lives -= 1
                target_pl.heal_if_needed()
                if any(
                    (
                        isinstance(c, grc.Talismano)
                        for c in target_pl.gold_rush_equipment
                    )
                ):
                    target_pl.gold_nuggets += 1
                if target_pl.character.check(self, grch.SimeonPicos):
                    target_pl.gold_nuggets += 1
                if any(
                    (isinstance(c, grc.Stivali) for c in target_pl.gold_rush_equipment)
                ):
                    self.deck.draw(True, player=target_pl)
                target_pl.notify_self()
                self.is_russian_roulette_on = False
                self.players[self.turn].play_turn()
            else:
                self.player_bangs += 1
                target_pl = pls[
                    (pls.index(self.players[self.turn]) + self.player_bangs) % len(pls)
                ]
                print(f"{self.name}: next in line {target_pl.name}")
                if target_pl.get_banged(self.deck.event_cards[0]):
                    target_pl.notify_self()
                else:
                    self.responders_did_respond_resume_turn(did_lose=True)
        else:
            self.ready_count += 1
            if self.ready_count == self.waiting_for:
                tmp = self.ready_count
                self.waiting_for = 0
                self.ready_count = 0
                self.attack_in_progress = False
                if self.pending_winners and not self.someone_won:
                    return self.announces_winners()
                if self.dalton_on:
                    self.dalton_on = False
                    print(
                        f"{self.name}: notifying {self.players[self.turn].name} about his turn"
                    )
                    self.players[self.turn].play_turn()
                elif self.poker_on and not any(
                    c.number == 1 for c in self.deck.scrap_pile[-tmp:]
                ):
                    self.players[self.turn].pending_action = pl.PendingAction.CHOOSE
                    self.players[
                        self.turn
                    ].choose_text = f"choose_from_poker;{min(2, tmp)}"
                    self.players[self.turn].available_cards = self.deck.scrap_pile[
                        -tmp:
                    ]
                elif self.attack_queue:
                    print("attack completed, next attack")
                    atk = self.attack_queue.pop(0)
                    self.attack(atk[0], atk[1], atk[2], atk[3], skip_queue=True)
                elif self.players[self.turn].pending_action == pl.PendingAction.CHOOSE:
                    self.players[self.turn].notify_self()
                else:
                    self.players[self.turn].pending_action = pl.PendingAction.PLAY
                self.poker_on = False
                self.players[self.turn].notify_self()

    def announces_winners(self, winners=None):
        """Announces the winners of the game in the chat"""
        if winners is None:
            print(f"{self.name}: WE HAVE A WINNER - pending winners")
        else:
            print(f"{self.name}: WE HAVE A WINNER")
        for p in self.players:
            if winners is None:
                p.win_status = p in self.pending_winners
            else:
                p.win_status = p in winners
            if p.win_status and not (isinstance(p.role, roles.Renegade) and p.is_dead):
                if not self.someone_won:
                    self.someone_won = True
                G.sio.emit(
                    "chat_message", room=self.name, data=f"_won|{p.name}|{p.role.name}"
                )
                if not self.is_replay:
                    Metrics.send_metric(
                        "player_win",
                        points=[1],
                        tags=[f"char:{p.character.name}", f"role:{p.role.name}"],
                    )
            p.notify_self()
        if hasattr(G.sio, "is_fake"):
            print(
                "announces_winners(): Running for tests, you will have to call reset manually!"
            )
            return
        for i in range(5):
            G.sio.emit("chat_message", room=self.name, data=f"_lobby_reset|{5-i}")
            eventlet.sleep(1)
        return self.reset()

    def next_player(self):
        """Returns the next player in turn order"""
        pls = self.get_alive_players()
        return pls[(pls.index(self.players[self.turn]) + 1) % len(pls)]

    def play_turn(self):
        """Starts the turn of the current player"""
        self.incremental_turn += 1
        if not self.is_replay:
            Metrics.send_metric(
                "incremental_turn",
                points=[self.incremental_turn],
                tags=[f"game:{self.SEED}"],
            )
        if self.players[self.turn].is_dead:
            pl = sorted(self.get_dead_players(), key=lambda x: x.death_turn)[0]
            if (
                self.check_event([ce.DeadMan, cew.Camposanto])
                and not self.did_resuscitate_deadman
                and pl == self.players[self.turn]
            ):
                print(f"{self.name}: {self.players[self.turn]} is dead, revive")
                if self.check_event(ce.DeadMan):
                    self.did_resuscitate_deadman = True
                    pl.lives = 2
                elif self.check_event(cew.Camposanto):
                    pl.lives = 1
                    pl.set_role = self.dead_roles.pop(
                        self.rng.randint(0, len(self.dead_roles) - 1)
                    )
                pl.is_dead = False
                pl.is_ghost = False
                self.deck.draw(player=pl)
                self.deck.draw(player=pl)
                if (
                    ghost := next(
                        (c for c in pl.equipment if isinstance(c, tvosc.Fantasma)), None
                    )
                ) is not None:
                    self.deck.scrap(ghost)
                    pl.equipment.remove(ghost)
                pl.notify_self()
            elif (
                self.check_event(ceh.CittaFantasma) or self.players[self.turn].is_ghost
            ):
                print(f"{self.name}: {self.players[self.turn]} is dead, event ghost")
                self.players[self.turn].is_ghost = True
            else:
                print(f"{self.name}: {self.players[self.turn]} is dead, next turn")
                return self.next_turn()
        self.player_bangs = 0
        if isinstance(self.players[self.turn].role, roles.Sheriff) or (
            (
                self.initial_players == 3
                and isinstance(self.players[self.turn].role, roles.Vice)
                and not self.players[self.turn].is_ghost
            )
            or (
                self.initial_players == 3
                and any(
                    (p for p in self.players if p.is_dead and p.role.name == "Vice")
                )
                and isinstance(self.players[self.turn].role, roles.Renegade)
            )
        ):
            self.deck.flip_event()
            self.deck.move_train_forward()
            if self.check_event(ce.RouletteRussa):
                self.is_russian_roulette_on = True
                if self.players[self.turn].get_banged(self.deck.event_cards[0]):
                    self.players[self.turn].notify_self()
                else:
                    self.responders_did_respond_resume_turn(did_lose=True)
                return
        if (
            self.check_event(ce.PerUnPugnoDiCarte)
            and len(self.players[self.turn].hand) > 0
        ):
            self.player_bangs = len(self.players[self.turn].hand)
            if self.players[self.turn].get_banged(self.deck.event_cards[0]):
                self.players[self.turn].notify_self()
            else:
                self.responders_did_respond_resume_turn()
        else:
            print(
                f"{self.name}: notifying {self.players[self.turn].name} about his turn"
            )
            self.players[self.turn].play_turn()

    def next_turn(self):
        if self.shutting_down:
            return
        print(f"{self.name}: {self.players[self.turn].name} invoked next turn")
        if self.pending_winners and not self.someone_won:
            return self.announces_winners()
        pls = self.get_alive_players()
        if len(pls) > 0:
            if self.check_event(ceh.CorsaAllOro):
                self.turn = (self.turn - 1) % len(self.players)
            else:
                self.turn = (self.turn + 1) % len(self.players)
            self.play_turn()

    def notify_event_card(self, sid=None):
        if len(self.deck.event_cards) > 0:
            room = self.name if sid is None else sid
            if self.deck.event_cards[0] is not None:
                G.sio.emit(
                    "event_card", room=room, data=self.deck.event_cards[0].__dict__
                )
            else:
                G.sio.emit("event_card", room=room, data=None)

    def notify_event_card_wildwestshow(self, sid=None):
        if len(self.deck.event_cards_wildwestshow) > 0:
            room = self.name if sid is None else sid
            if self.deck.event_cards_wildwestshow[0] is not None:
                G.sio.emit(
                    "event_card_wildwestshow",
                    room=room,
                    data=self.deck.event_cards_wildwestshow[0].__dict__,
                )
            else:
                G.sio.emit("event_card_wildwestshow", room=room, data=None)

    def notify_gold_rush_shop(self, sid=None):
        if (
            "gold_rush" in self.expansions
            and self.deck
            and self.deck.shop_cards
            and len(self.deck.shop_cards) > 0
        ):
            room = self.name if sid is None else sid
            print(
                f"{self.name}: gold_rush_shop room={room}, data={self.deck.shop_cards}"
            )
            G.sio.emit(
                "gold_rush_shop",
                room=room,
                data=json.dumps(self.deck.shop_cards, default=lambda o: o.__dict__),
            )

    def notify_stations(self, sid=None):
        if "train_robbery" in self.expansions:
            room = self.name if sid is None else sid
            G.sio.emit(
                "stations",
                room=room,
                data=json.dumps(
                    {
                        "stations": self.deck.stations,
                        "current_train": self.deck.current_train,
                    },
                    default=lambda o: o.__dict__,
                ),
            )

    def notify_scrap_pile(self, sid=None):
        print(f"{self.name}: scrap")
        room = self.name if sid is None else sid
        if self.deck.peek_scrap_pile():
            G.sio.emit("scrap", room=room, data=self.deck.peek_scrap_pile().__dict__)
        else:
            G.sio.emit("scrap", room=room, data=None)

    def handle_disconnect(self, player: pl.Player):
        print(f"{self.name}: player {player.name} left the game")
        if player in self.spectators:
            self.spectators.remove(player)
            G.sio.emit("spectators", room=self.name, data=len(self.spectators))
            return False
        if player.is_bot and not self.started:
            player.game = None
        if self.disconnect_bot and self.started:
            player.is_bot = True
            if not any((not p.is_bot for p in self.players)):
                eventlet.sleep(5)
                if not any((not p.is_bot for p in self.players)):
                    print(f"{self.name}: no players left in game, shutting down")
                    self.shutting_down = True
                    self.players = []
                    self.spectators = []
                    self.deck = None
                    return True
            eventlet.sleep(15)  # he may reconnect
            if player.is_bot:
                player.was_player = False
                if len(player.available_characters) > 0:
                    player.set_available_character(player.available_characters)
                G.sio.start_background_task(player.bot_spin)
        else:
            self.player_death(player=player, disconnected=True)
        # else:
        #     player.lives = 0
        # self.players.remove(player)
        if not any((not p.is_bot for p in self.players)):
            print(f"{self.name}: no players left in game, shutting down")
            self.shutting_down = True
            self.players = []
            self.spectators = []
            self.deck = None
            return True
        else:
            return False

    def player_death(self, player: pl.Player, disconnected=False):
        if not player in self.players or player.is_ghost:
            return
        self.is_handling_death = True
        import bang.expansions.dodge_city.characters as chd

        print(f"{self.name}: the killer is {player.attacker}")
        if player.character and player.role:
            if not self.is_replay:
                Metrics.send_metric(
                    "player_death",
                    points=[1],
                    tags=[f"char:{player.character.name}", f"role:{player.role.name}"],
                )
        if (
            any((isinstance(c, grc.Ricercato) for c in player.gold_rush_equipment))
            and player.attacker
            and player.attacker in self.players
        ):
            player.attacker.gold_nuggets += 1
            self.deck.draw(True, player=player.attacker)
            self.deck.draw(True, player=player.attacker)
            player.attacker.notify_self()
        # se lo sceriffo uccide il proprio vice
        if (
            player.attacker
            and player.attacker in self.players
            and isinstance(player.attacker.role, roles.Sheriff)
            and isinstance(player.role, roles.Vice)
        ):
            for i in range(len(player.attacker.hand)):
                self.deck.scrap(
                    player.attacker.hand.pop(), True, player=player.attacker
                )
            for i in range(len(player.attacker.equipment)):
                self.deck.scrap(
                    player.attacker.equipment.pop(), True, player=player.attacker
                )
            for i in range(len(player.attacker.gold_rush_equipment)):
                self.deck.shop_deck.append(player.attacker.gold_rush_equipment.pop())
            player.attacker.notify_self()
        elif (
            player.attacker
            and player.attacker in self.players
            and (isinstance(player.role, roles.Outlaw) or self.initial_players == 3)
        ):
            for i in range(3):
                self.deck.draw(True, player=player.attacker)
            player.attacker.notify_self()
        print(f"{self.name}: player {player.name} died")
        if self.waiting_for > 0 and player.pending_action == pl.PendingAction.RESPOND:
            self.responders_did_respond_resume_turn()
            player.pending_action = pl.PendingAction.WAIT

        if player.is_dead:
            return
        if not self.started:
            self.players.remove(player)
        elif disconnected:
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
        self.dead_roles.append(player.role)
        G.sio.emit("chat_message", room=self.name, data=f"_died|{player.name}")
        for p in self.players:
            if not p.is_bot:
                p.notify_self()
        # self.players_map = {c.name: i for i, c in enumerate(self.players)}
        if self.started:
            G.sio.emit(
                "chat_message",
                room=self.name,
                data=f"_died_role|{player.name}|{player.role.name}",
            )
            print(f"{self.name}: Check win status")
            attacker_role = None
            if player.attacker and player.attacker in self.players:
                attacker_role = player.attacker.role
            winners = [
                p
                for p in self.players
                if p.role is not None
                and p.role.on_player_death(
                    [p for p in self.get_alive_players() if not p.is_ghost],
                    initial_players=self.initial_players,
                    dead_role=player.role,
                    attacker_role=attacker_role,
                )
            ]
            if (
                not self.attack_in_progress
                and len(winners) > 0
                and not self.someone_won
            ):
                return self.announces_winners(winners)
            elif (
                len(winners) > 0 and not self.someone_won
            ):  # non tutti hanno risposto, ma ci sono vincitori.
                self.pending_winners = winners
            else:
                if (
                    not isinstance(player.role, roles.Sheriff)
                    and not self.initial_players == 3
                ):
                    G.sio.emit(
                        "notify_dead_role",
                        room=self.name,
                        data={
                            "name": player.name,
                            "lives": 0,
                            "max_lives": player.max_lives,
                            "is_ghost": player.is_ghost,
                            "is_bot": player.is_bot,
                            "icon": "🤠",
                            "avatar": player.avatar,
                            "role": player.role.__dict__,
                        },
                    )

            for i in range(len(player.gold_rush_equipment)):
                self.deck.shop_deck.append(
                    player.gold_rush_equipment.pop()
                )  # vulture sam doesnt get these cards

            # il giocatore quando muore perde tutte le pepite se non è pistolero ombra
            player.gold_nuggets = 0

            vulture = [
                p
                for p in self.get_alive_players()
                if p.character.check(self, characters.VultureSam)
            ]
            if len(vulture) == 0:
                for i in range(len(player.hand)):
                    self.deck.scrap(player.hand.pop(), True)
                for i in range(len(player.equipment)):
                    self.deck.scrap(player.equipment.pop(), True)
            elif len(vulture) == 2:
                for i in range(len(player.hand)):
                    vulture[i % 2].hand.append(player.hand.pop())
                    vulture[i % 2].hand[-1].reset_card()
                for i in range(len(player.equipment)):
                    vulture[i % 2].hand.append(player.equipment.pop())
                    vulture[i % 2].hand[-1].reset_card()
                vulture[0].notify_self()
                vulture[1].notify_self()
            else:
                for i in range(len(player.hand)):
                    vulture[0].hand.append(player.hand.pop())
                    vulture[0].hand[-1].reset_card()
                for i in range(len(player.equipment)):
                    vulture[0].hand.append(player.equipment.pop())
                    vulture[0].hand[-1].reset_card()
                vulture[0].notify_self()

            greg = [
                p
                for p in self.get_alive_players()
                if p.character.check(self, chd.GregDigger)
            ]
            for i in range(len(greg)):
                greg[i].lives = min(greg[i].lives + 2, greg[i].max_lives)
            herb = [
                p
                for p in self.get_alive_players()
                if p.character.check(self, chd.HerbHunter)
            ]
            for i in range(len(herb)):
                self.deck.draw(True, player=herb[i])
                self.deck.draw(True, player=herb[i])
                herb[i].notify_self()

            # se Vulture Sam o Herb Hounter è uno sceriffo e ha appena ucciso il suo Vice, deve scartare le carte che ha pescato con la sua abilità
            if (
                player.attacker
                and player.attacker in self.get_alive_players()
                and isinstance(player.attacker.role, roles.Sheriff)
                and isinstance(player.role, roles.Vice)
            ):
                for i in range(len(player.attacker.hand)):
                    self.deck.scrap(player.attacker.hand.pop(), True)
                player.attacker.notify_self()

        self.is_handling_death = False
        if corpse.is_my_turn:
            corpse.is_my_turn = False
            corpse.notify_self()
            self.next_turn()

    def check_event(self, ev):
        if self.deck is None:
            return False
        if isinstance(ev, type):
            return (
                len(self.deck.event_cards) > 0
                and isinstance(self.deck.event_cards[0], ev)
            ) or (
                len(self.deck.event_cards_wildwestshow) > 0
                and isinstance(self.deck.event_cards_wildwestshow[0], ev)
            )
        else:
            return any(self.check_event(evc) for evc in ev)

    def get_visible_players(
        self, player: pl.Player
    ):  # returns a dictionary because we need to add the distance
        pls = self.get_alive_players()
        if len(pls) == 0 or player not in pls:
            return []
        i = pls.index(player)
        mindist = 99 if not self.check_event(ce.Agguato) else 1
        return [
            {
                "name": pls[j].name,
                "dist": min(
                    [
                        abs(i - j),
                        (i + abs(j - len(pls))),
                        (j + abs(i - len(pls))),
                        mindist,
                    ]
                )
                + pls[j].get_visibility(),
                "lives": pls[j].lives,
                "max_lives": pls[j].max_lives,
                "is_sheriff": isinstance(pls[j].role, roles.Sheriff),
                "cards": len(pls[j].hand) + len(pls[j].equipment),
                "is_ghost": pls[j].is_ghost,
                "is_bot": pls[j].is_bot,
                "icon": pls[j].role.icon
                if (
                    pls[j].role is not None
                    and (
                        self.initial_players == 3
                        or isinstance(pls[j].role, roles.Sheriff)
                    )
                )
                else "🤠",
                "avatar": pls[j].avatar,
                "role": pls[j].role,
            }
            for j in range(len(pls))
            if i != j
        ]

    def get_alive_players(self):
        return [p for p in self.players if not p.is_dead or p.is_ghost]

    def get_dead_players(self, include_ghosts=True):
        return [
            p for p in self.players if p.is_dead and (include_ghosts or not p.is_ghost)
        ]

    def notify_all(self):
        if self.started and self.replay_speed > 0:
            show_cards = self.check_event(cew.Sacagaway)
            data = [
                {
                    "name": p.name,
                    "ncards": len(p.hand),
                    "hand_cards": [c.__dict__ for c in p.hand] if show_cards else [],
                    "equipment": [e.__dict__ for e in p.equipment],
                    "gold_rush_equipment": [e.__dict__ for e in p.gold_rush_equipment],
                    "lives": p.lives,
                    "max_lives": p.max_lives,
                    "gold_nuggets": p.gold_nuggets,
                    "is_sheriff": isinstance(p.role, roles.Sheriff),
                    "is_my_turn": p.is_my_turn,
                    "pending_action": p.pending_action,
                    "character": p.character.__dict__ if p.character else None,
                    "real_character": p.real_character.__dict__
                    if p.real_character
                    else None,
                    "icon": p.role.icon
                    if self.initial_players == 3 and p.role
                    else "🤠",
                    "avatar": p.avatar,
                    "is_ghost": p.is_ghost,
                    "is_bot": p.is_bot,
                }
                for p in self.get_alive_players()
            ]
            G.sio.emit("players_update", room=self.name, data=data)

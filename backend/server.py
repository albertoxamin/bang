import faulthandler
import json
import logging
import os
import pickle
import random
import sys
import traceback
import urllib.parse
from functools import wraps
from typing import List

import eventlet
import requests
import socketio
from discord_webhook import DiscordWebhook

from bang.game import Game
from bang.players import PendingAction, Player
from globals import G
from metrics import Metrics

sys.setrecursionlimit(10**6)  # this should prevents bots from stopping


logging.basicConfig(filename="out.log", level="ERROR")


Metrics.init()

sio = socketio.Server(cors_allowed_origins="*")
G.sio = sio


faulthandler.enable()

static_files = {
    "/": {"content_type": "text/html", "filename": "index.html"},
    "/game": {"content_type": "text/html", "filename": "index.html"},
    "/help": {"content_type": "text/html", "filename": "index.html"},
    "/status": {"content_type": "text/html", "filename": "index.html"},
    # '/robots.txt': {'content_type': 'text/html', 'filename': 'robots.txt'},
    "/favicon.ico": {"filename": "favicon.ico"},
    "/img/icons": "./img/icons",
    "/manifest.webmanifest": {"filename": "manifest.webmanifest"},
    "/assets": "./assets",
    #'/css': './css',
    #'/media': './media',
    #'/js': './js',
}
if "UseRobots" in os.environ and os.environ["UseRobots"].upper() == "TRUE":
    static_files["/robots.txt"] = {
        "content_type": "text/html",
        "filename": "robots.txt",
    }

for file in [f for f in os.listdir(".") if ".js" in f or ".map" in f or ".html" in f]:
    static_files[f"/{file}"] = f"./{file}"

HASTEBIN_HEADERS = {
    "Authorization": "Bearer " + os.getenv("HASTEBIN_TOKEN", ""),
    "content-type": "text/plain",
}

app = socketio.WSGIApp(sio, static_files=static_files)
games: dict[str, Game] = {}
online_players = 0
blacklist: List[str] = []


def send_to_debug(error):
    for g in games.values():
        if g.debug:
            sio.emit(
                "chat_message",
                room=g.name,
                data={
                    "color": "red",
                    "text": json.dumps({"ERROR": error}),
                    "type": "json",
                },
            )
        elif any((p.is_admin() for p in g.players)):
            for p in g.players:
                if p.is_admin():
                    sio.emit(
                        "chat_message",
                        room=p.sid,
                        data={
                            "color": "red",
                            "text": json.dumps({"ERROR": error}),
                            "type": "json",
                        },
                    )


SAVE_LOCK = False


def bang_handler(func):
    """Decorator to handle exceptions in custom sockets handlers."""

    @wraps(func)
    def wrapper_func(*args, **kwargs):
        global SAVE_LOCK
        SAVE_LOCK = True
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            print(traceback.format_exc())
            send_to_debug(traceback.format_exc())
        finally:
            SAVE_LOCK = False

    return wrapper_func


def count_bots_in_game(game):
    """Count the number of bots in a game."""
    return sum(1 for p in game.players if p.is_bot)


def advertise_lobbies():
    open_lobbies = [
        g for g in games.values() if 0 < len(g.players) < 10 and not g.is_hidden
    ][-10:]
    sio.emit(
        "lobbies",
        room="lobby",
        data=[
            {
                "name": g.name,
                "players": len(g.players),
                "bots": count_bots_in_game(g),
                "locked": g.password != "",
                "expansions": g.expansions,
            }
            for g in open_lobbies
            if not g.started
        ],
    )
    sio.emit(
        "spectate_lobbies",
        room="lobby",
        data=[
            {
                "name": g.name,
                "players": len(g.players),
                "bots": count_bots_in_game(g),
                "locked": g.password != "",
                "expansions": g.expansions,
            }
            for g in open_lobbies
            if g.started
        ],
    )
    Metrics.send_metric(
        "lobbies", points=[sum(not g.is_replay for g in games.values())]
    )
    Metrics.send_metric("online_players", points=[online_players])


@sio.event
@bang_handler
def connect(sid, environ):
    global online_players
    online_players += 1
    print("connect ", sid)
    sio.enter_room(sid, "lobby")
    sio.emit("players", room="lobby", data=online_players)
    Metrics.send_metric("online_players", points=[online_players])


@sio.event
@bang_handler
def get_online_players(sid):
    global online_players
    sio.emit("players", room="lobby", data=online_players)


@sio.event
@bang_handler
def report(sid, text):
    print(f"New report from {sid}: {text}")
    ses: Player = sio.get_session(sid)
    data = ""
    if hasattr(ses, "game"):
        data = "\n".join(ses.game.rpc_log[:-1]).strip()
    data = data + "\n@@@\n" + text
    response = requests.post(
        "https://hastebin.com/documents", data.encode("utf-8"), headers=HASTEBIN_HEADERS
    )
    key = json.loads(response.text).get("key")
    if "DISCORD_WEBHOOK" in os.environ and len(os.environ["DISCORD_WEBHOOK"]) > 0:
        webhook = DiscordWebhook(
            url=os.environ["DISCORD_WEBHOOK"],
            content=f"New bug reported by {ses.name}, replay at https://bang.xamin.it/game?replay={key}\nRaw: https://hastebin.com/{key}\nTotal actions:{len(ses.game.rpc_log)}\nExpansions:{ses.game.expansions}\nInfo: {text}",
        )
        response = webhook.execute()
        sio.emit(
            "chat_message", room=sid, data={"color": f"green", "text": f"Report OK"}
        )
        if not any((p.pending_action != PendingAction.WAIT for p in ses.game.players)):
            sio.emit(
                "chat_message",
                room=ses.game.name,
                data={
                    "color": "red",
                    "text": f"TRYING AUTO FIX BY KICKING THE ARCADE CABINET",
                },
            )
            ses.game.next_turn()
            if any((p.pending_action == PendingAction.WAIT for p in ses.game.players)):
                sio.emit(
                    "chat_message",
                    room=ses.game.name,
                    data={
                        "color": f"green",
                        "text": f"IT WORKED!11!!!, we will still fix the bug (for real) though",
                    },
                )
    else:
        print("WARNING: DISCORD_WEBHOOK not found")
    Metrics.send_event("BUG_REPORT", event_data=text)
    print(f"New bug report, replay at https://bang.xamin.it/game?replay={key}")


@sio.event
@bang_handler
def set_username(sid, username):
    ses = sio.get_session(sid)
    if not isinstance(ses, Player):
        dt = username["discord_token"] if "discord_token" in username else None
        sio.save_session(
            sid, Player(username.get("name", "player"), sid, discord_token=dt)
        )
        print(f"{sid} is now {username}")
        advertise_lobbies()
    elif ses.game is None or not ses.game.started:
        username = username["name"]
        print(f"{sid} changed username to {username}")
        prev = ses.name
        if ses.game and any((p.name == username for p in ses.game.players)):
            ses.name = f"{username}_{random.randint(0,100)}"
        else:
            ses.name = username
        sio.emit(
            "chat_message",
            room=ses.game.name,
            data=f"_change_username|{prev}|{ses.name}",
        )
        sio.emit("me", data=ses.name, room=sid)
        ses.game.notify_room()


@sio.event
@bang_handler
def get_me(sid, data):
    if isinstance(sio.get_session(sid), Player):
        sio.emit("me", data=sio.get_session(sid).name, room=sid)
        if sio.get_session(sid).game:
            sio.get_session(sid).game.notify_room()
    else:
        dt = data.get("discord_token", None)
        username = data.get("username", None)
        if username is None:
            username = f"player_{random.randint(0,100)}"
        sio.save_session(sid, Player(username, sid, discord_token=dt))
        p = sio.get_session(sid)
        print(f"{sid} is now {username}")
        if "replay" in data and data["replay"] is not None:
            create_room(sid, data["replay"])
            p.game.is_hidden = True
            eventlet.sleep(0.5)
            response = requests.get(
                f"https://hastebin.com/raw/{data['replay']}",
                headers=HASTEBIN_HEADERS,
                timeout=3,
            )
            if response.status_code != 200:
                sio.emit(
                    "chat_message",
                    room=sid,
                    data={"color": f"green", "text": f"Invalid replay code"},
                )
                return
            log = response.text.splitlines()
            p.game.spectators.append(p)
            if "ffw" not in data:
                p.game.replay(log)
            else:
                p.game.replay(log, speed=0, fast_forward=int(data["ffw"]))
            return
        if data["name"] in games and (room := games[data["name"]]) is not None:
            if not room.started:
                join_room(sid, data)
            elif room.started:
                print("room exists")
                if username != "player" and any(
                    (
                        p.name == username
                        for p in room.players
                        if (
                            p.is_bot
                            or (dt is not None and p.discord_token == dt)
                            or p.sid is None
                        )
                    )
                ):
                    print("getting inside the bot")
                    bot = [
                        p
                        for p in room.players
                        if (
                            p.is_bot
                            or (dt is not None and p.discord_token == dt)
                            or p.sid is None
                        )
                        and p.name == username
                    ][0]
                    bot.sid = sid
                    bot.is_bot = False
                    sio.enter_room(sid, room.name)
                    sio.save_session(sid, bot)
                    room.notify_room(sid)
                    eventlet.sleep(0.1)
                    room.notify_all()
                    room.notify_scrap_pile(sid)
                    sio.emit(
                        "role",
                        room=sid,
                        data=json.dumps(bot.role, default=lambda o: o.__dict__),
                    )
                    bot.notify_self()
                    if len(bot.available_characters) > 0:
                        bot.set_available_character(bot.available_characters)
                else:  # spectate
                    room.spectators.append(sio.get_session(sid))
                    sio.get_session(sid).game = room
                    sio.enter_room(sid, room.name)
                    room.notify_room(sid)
                    eventlet.sleep(0.1)
                    room.notify_event_card(sid)
                    room.notify_event_card_wildwestshow(sid)
                    room.notify_scrap_pile(sid)
                    room.notify_all()
                room.notify_gold_rush_shop()
                room.notify_stations()
                room.notify_event_card()
                room.notify_event_card_wildwestshow(sid)
        else:
            create_room(sid, data["name"])
        p: Player = sio.get_session(sid)
        if p.game is None:
            sio.emit("me", data={"error": "Wrong password/Cannot connect"}, room=sid)
        else:
            sio.emit("me", data=p.name, room=sid)
            if username == "player" or any(
                (
                    pl.name == username
                    for pl in p.game.players
                    if not (
                        (dt is not None and pl.discord_token == dt)
                        or pl.sid is None
                        or pl == p
                    )
                )
            ):
                sio.emit("change_username", room=sid)
            elif p.name != username:
                sio.emit(
                    "chat_message",
                    room=p.game.name,
                    data=f"_change_username|{p.name}|{username}",
                )
                p.name = data["username"]
                sio.emit("me", data=p.name, room=sid)
                if not p.game.started:
                    p.game.notify_room()


@sio.event
@bang_handler
def disconnect(sid):
    global online_players
    online_players -= 1
    if (p := sio.get_session(sid)) is not None and isinstance(p, Player):
        sio.emit("players", room="lobby", data=online_players)
        if p.game and p.disconnect():
            sio.close_room(p.game.name)
            games.pop(p.game.name)
        print("disconnect ", sid)
        advertise_lobbies()
    Metrics.send_metric("online_players", points=[online_players])


@sio.event
@bang_handler
def create_room(sid, room_name):
    if (p := sio.get_session(sid)).game is None:
        while room_name in games:
            room_name += f"_{random.randint(0, 10000)}"
        sio.leave_room(sid, "lobby")
        sio.enter_room(sid, room_name)
        g = Game(room_name)
        g.add_player(p)
        if room_name in blacklist:
            g.is_hidden = True
        games[room_name] = g
        print(f"{sid} created a room named {room_name}")
        advertise_lobbies()


@sio.event
@bang_handler
def private(sid):
    g = sio.get_session(sid).game
    g.set_private()
    advertise_lobbies()


@sio.event
@bang_handler
def toggle_expansion(sid, expansion_name):
    game = sio.get_session(sid).game
    if "suggest" in expansion_name:
        sio.emit("suggest_expansion", room=game.name, data=expansion_name.split(";")[1])
        return
    game.toggle_expansion(expansion_name)
    advertise_lobbies()


@sio.event
@bang_handler
def toggle_comp(sid):
    sio.get_session(sid).game.toggle_competitive()


@sio.event
@bang_handler
def toggle_replace_with_bot(sid):
    sio.get_session(sid).game.toggle_disconnect_bot()


@sio.event
@bang_handler
def join_room(sid, room):
    room_name = room["name"]
    pwd = room.get("password", "")
    if pwd is None:
        pwd = ""
    if games[room_name].password != "" and games[room_name].password != pwd.upper():
        return
    player = sio.get_session(sid)
    if not games[room_name].started:
        print(f"{sid} joined a room named {room_name}")
        sio.leave_room(sid, "lobby")
        sio.enter_room(sid, room_name)
        while any(
            (p.name == player.name and not p.is_bot for p in games[room_name].players)
        ):
            player.name += f"_{random.randint(0,100)}"
        sio.emit("me", data=player.name, room=sid)
        games[room_name].add_player(player)
        advertise_lobbies()
    else:
        games[room_name].spectators.append(player)
        player.game = games[room_name]
        player.pending_action = PendingAction.WAIT
        sio.enter_room(sid, games[room_name].name)
        games[room_name].notify_room(sid)
        eventlet.sleep(0.5)
        games[room_name].notify_room(sid)
        games[room_name].notify_all()


"""
Sockets for the status page
"""


@sio.event
@bang_handler
def get_all_rooms(sid, deploy_key):
    ses = sio.get_session(sid)
    if ("DEPLOY_KEY" in os.environ and deploy_key == os.environ["DEPLOY_KEY"]) or (
        isinstance(ses, Player) and ses.is_admin()
    ):
        sio.emit(
            "all_rooms",
            room=sid,
            data=[
                {
                    "name": g.name,
                    "hidden": g.is_hidden,
                    "players": [
                        {
                            "name": p.name,
                            "bot": p.is_bot,
                            "health": p.lives,
                            "sid": p.sid,
                        }
                        for p in g.players
                    ],
                    "password": g.password,
                    "expansions": g.expansions,
                    "started": g.started,
                    "current_turn": g.turn,
                    "incremental_turn": g.incremental_turn,
                    "debug": g.debug,
                    "spectators": len(g.spectators),
                }
                for g in games.values()
            ],
        )


@sio.event
@bang_handler
def kick(sid, data):
    ses = sio.get_session(sid)
    if (
        "DEPLOY_KEY" in os.environ
        and "key" in data
        and data["key"] == os.environ["DEPLOY_KEY"]
    ) or (isinstance(ses, Player) and ses.is_admin()):
        sio.emit("kicked", room=data["sid"])


@sio.event
@bang_handler
def reset(sid, data):
    global games
    ses = sio.get_session(sid)
    if (
        "DEPLOY_KEY" in os.environ
        and "key" in data
        and data["key"] == os.environ["DEPLOY_KEY"]
    ) or (isinstance(ses, Player) and ses.is_admin()):
        for g in games.values():
            sio.emit("kicked", room=g.name)
        games = {}


@sio.event
@bang_handler
def hide_toogle(sid, data):
    ses = sio.get_session(sid)
    if (
        "DEPLOY_KEY" in os.environ
        and "key" in data
        and data["key"] == os.environ["DEPLOY_KEY"]
    ) or (isinstance(ses, Player) and ses.is_admin()):
        game = games["room"]
        if len(games) > 0:
            game[0].is_hidden = not game[0].is_hidden
            if game[0].is_hidden:
                if not data["room"] in blacklist:
                    blacklist.append(data["room"])
            elif data["room"] in blacklist:
                blacklist.remove(data["room"])
            advertise_lobbies()


"""
Sockets for the game
"""


@sio.event
@bang_handler
def start_game(sid):
    ses: Player = sio.get_session(sid)
    ses.game.start_game()
    advertise_lobbies()


@sio.event
@bang_handler
def shuffle_players(sid):
    ses: Player = sio.get_session(sid)
    ses.game.shuffle_players()


@sio.event
@bang_handler
def set_character(sid, name):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};set_character;{name}")
    if not ses.game.is_replay:
        Metrics.send_metric("set_character", points=[1], tags=[f"char:{name}"])
    ses.set_character(name)


@sio.event
@bang_handler
def refresh(sid):
    ses: Player = sio.get_session(sid)
    ses.notify_self()


@sio.event
@bang_handler
def draw(sid, pile):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};draw;{pile}")
    ses.draw(pile)


@sio.event
@bang_handler
def pick(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};pick")
    ses.pick()


@sio.event
@bang_handler
def end_turn(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};end_turn")
    ses.end_turn()


@sio.event
@bang_handler
def play_card(sid, data):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};play_card;{json.dumps(data)}")
    ses.play_card(data["index"], data["against"], data["with"])


@sio.event
@bang_handler
def respond(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};respond;{card_index}")
    ses.respond(card_index)


@sio.event
@bang_handler
def choose(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};choose;{card_index}")
    ses.choose(card_index)


@sio.event
@bang_handler
def scrap(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};scrap;{card_index}")
    ses.scrap(card_index)


@sio.event
def special(sid, data):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};special;{json.dumps(data)}")
    ses.special(data)


@sio.event
@bang_handler
def gold_rush_discard(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};gold_rush_discard;")
    ses.gold_rush_discard()


@sio.event
@bang_handler
def buy_gold_rush_card(sid, data: int):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};buy_gold_rush_card;{data}")
    ses.buy_gold_rush_card(data)


@sio.event
@bang_handler
def buy_train(sid, data: int):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f"{ses.name};buy_train;{data}")
    ses.buy_train(data)


@sio.event
@bang_handler
def chat_message(sid, msg, pl=None):
    ses: Player = sio.get_session(sid) if pl is None else pl
    ses.game.rpc_log.append(f"{ses.name};chat_message;{msg}")
    if len(msg) > 0:
        if msg[0] == "/":
            commands = msg.split(";")
            for msg in commands:
                if "/addbot" in msg and not ses.game.started:
                    if len(msg.split()) > 1:
                        sio.emit(
                            "chat_message",
                            room=ses.game.name,
                            data={"color": "red", "text": "Only 1 bot at the time"},
                        )
                    else:
                        bot = Player(f"AI_{random.randint(0,10)}", "bot", bot=True)
                        while any((p for p in ses.game.players if p.name == bot.name)):
                            bot = Player(f"AI_{random.randint(0,10)}", "bot", bot=True)
                        ses.game.add_player(bot)
                        advertise_lobbies()
                        sio.start_background_task(bot.bot_spin)
                    return
                if (
                    "/replay" in msg
                    and not "/replayspeed" in msg
                    and not "/replaypov" in msg
                ):
                    _cmd = msg.split()
                    if len(_cmd) >= 2:
                        replay_id = _cmd[1]
                        response = requests.get(
                            f"https://hastebin.com/raw/{replay_id}",
                            headers=HASTEBIN_HEADERS,
                            timeout=5,
                        )
                        log = response.text.splitlines()
                        ses.game.spectators.append(ses)
                        if len(_cmd) == 2:
                            ses.game.replay(log)
                        if len(_cmd) == 3:
                            line = int(_cmd[2])
                            ses.game.replay(log, speed=0, fast_forward=line)
                    return
                if "/replayspeed" in msg:
                    _cmd = msg.split()
                    if len(_cmd) == 2:
                        ses.game.replay_speed = float(_cmd[1])
                    return
                if "/replaypov" in msg:
                    _cmd = msg.split()
                    if len(_cmd) > 1:
                        name = " ".join(_cmd[1:])
                        for p in ses.game.players:
                            if p.sid == ses.sid:
                                p.sid = ""
                        pl = ses.game.get_player_named(name)
                        pl.sid = ses.sid
                        pl.set_role(pl.role)
                        pl.notify_self()
                    return
                if "/startwithseed" in msg and not ses.game.started:
                    if len(msg.split()) > 1:
                        ses.game.start_game(int(msg.split()[1]))
                    return
                if "/removebot" in msg and not ses.game.started:
                    if any((p.is_bot for p in ses.game.players)):
                        [p for p in ses.game.players if p.is_bot][-1].disconnect()
                    advertise_lobbies()
                    return
                if "/togglecomp" in msg and ses.game:
                    ses.game.toggle_competitive()
                    return
                elif "/set_chars" in msg and not ses.game.started:
                    cmd = msg.split()
                    if len(cmd) == 2 and int(cmd[1]) > 0:
                        ses.game.characters_to_distribute = int(cmd[1])
                        ses.game.notify_room()
                    return
                if "/debug" in msg:
                    cmd = msg.split()
                    if (
                        len(cmd) == 2
                        and "DEPLOY_KEY" in os.environ
                        and cmd[1] == os.environ["DEPLOY_KEY"]
                    ):  # solo chi ha la deploy key può attivare la modalità debug
                        ses.game.debug = not ses.game.debug
                        ses.game.notify_room()
                    elif (
                        ses == ses.game.players[0] or ses.is_admin()
                    ):  # solo l'owner può attivare la modalità debug
                        ses.game.debug = not ses.game.debug
                        ses.game.notify_room()
                    if ses.game.debug:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={
                                "color": "red",
                                "text": "debug mode is now active, only the owner of the room can disable it with /debug",
                            },
                        )
                    return
                if not ses.game.debug and not ses.is_admin():
                    sio.emit(
                        "chat_message",
                        room=sid,
                        data={
                            "color": "",
                            "text": "debug mode is not active, only the owner of the room can enable it with /debug",
                        },
                    )
                elif "/suicide" in msg and ses.game.started and ses.lives > 0:
                    ses.lives = 0
                    ses.notify_self()
                elif "/nextevent" in msg and ses.game.started:
                    ses.game.deck.flip_event()
                elif "/notify" in msg and ses.game.started:
                    cmd = msg.split()
                    if len(cmd) >= 3:
                        if cmd[1] in ses.game.players_map:
                            ses.game.get_player_named(cmd[1]).notify_card(
                                ses,
                                {
                                    "name": " ".join(cmd[2:]),
                                    "icon": "🚨",
                                    "suit": 4,
                                    "number": " ".join(cmd[2:]),
                                },
                            )
                    else:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={"color": "", "text": f"{msg} bad format"},
                        )
                elif "/show_cards" in msg and ses.game.started:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        if cmd[1] in ses.game.players_map:
                            sio.emit(
                                "chat_message",
                                room=ses.game.name,
                                data={
                                    "color": "red",
                                    "text": f"🚨 {ses.name} is in debug mode and is looking at {cmd[1]} hand",
                                },
                            )
                            for c in ses.game.get_player_named(cmd[1]).hand:
                                ses.notify_card(ses, c)
                                eventlet.sleep(0.3)
                    else:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={"color": "", "text": f"{msg} bad format"},
                        )
                elif (
                    "/ddc" in msg and ses.game.started
                ):  # debug destroy cards usage: [/ddc *] [/ddc username]
                    cmd = msg.split()
                    if len(cmd) == 2:
                        sio.emit(
                            "chat_message",
                            room=ses.game.name,
                            data={
                                "color": "red",
                                "text": f"🚨 {ses.name} is in debug mode destroyed {cmd[1]} cards",
                            },
                        )
                        if cmd[1] == "*":
                            for p in ses.game.players_map:
                                ses.game.get_player_named(p).hand = []
                                ses.game.get_player_named(p).equipment = []
                                ses.game.get_player_named(p).notify_self()
                        elif cmd[1] in ses.game.players_map:
                            ses.game.get_player_named(cmd[1]).hand = []
                            ses.game.get_player_named(cmd[1]).equipment = []
                            ses.game.get_player_named(cmd[1]).notify_self()
                    else:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={"color": "", "text": f"{msg} bad format"},
                        )
                elif (
                    "/dsh" in msg and ses.game.started
                ):  # debug set health usage [/dsh * hp] [/dsh username hp]
                    cmd = msg.split()
                    if len(cmd) == 3:
                        sio.emit(
                            "chat_message",
                            room=ses.game.name,
                            data={
                                "color": "red",
                                "text": f"🚨 {ses.name} is in debug mode and is changing {cmd[1]} health",
                            },
                        )
                        if cmd[1] == "*":
                            for p in ses.game.players_map:
                                ses.game.get_player_named(p).lives = min(
                                    int(cmd[2]), ses.game.get_player_named(p).max_lives
                                )
                                ses.game.get_player_named(p).notify_self()
                        elif cmd[1] in ses.game.players_map:
                            ses.game.get_player_named(cmd[1]).lives = min(
                                int(cmd[2]), ses.game.get_player_named(cmd[1]).max_lives
                            )
                            ses.game.get_player_named(cmd[1]).notify_self()
                    else:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={"color": "", "text": f"{msg} bad format"},
                        )
                elif "/togglebot" in msg and ses.game:
                    ses.game.toggle_disconnect_bot()
                elif "/cancelgame" in msg and ses.game.started:
                    sio.emit(
                        "chat_message",
                        room=ses.game.name,
                        data={
                            "color": "red",
                            "text": f"🚨 {ses.name} stopped the current game",
                        },
                    )
                    ses.game.reset()
                elif "/startgame" in msg and not ses.game.started:
                    ses.game.start_game()
                elif "/setbotspeed" in msg:
                    ses.game.bot_speed = float(msg.split()[1])
                elif "/addex" in msg and not ses.game.started:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        cmd[1] = cmd[1].replace("foc", "fistful_of_cards")
                        if cmd[1] not in ses.game.available_expansions:
                            ses.game.available_expansions.append(cmd[1])
                            ses.game.notify_room()
                    else:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={"color": "", "text": f"{msg} bad format"},
                        )
                elif "/setcharacter" in msg:
                    import bang.characters as characters

                    cmd = msg.split()
                    if len(cmd) >= 2:
                        sio.emit(
                            "chat_message",
                            room=ses.game.name,
                            data={
                                "color": "red",
                                "text": f"🚨 {ses.name} is in debug mode and changed character",
                            },
                        )
                        chs = characters.all_characters(ses.game.expansions)
                        ses.character = [c for c in chs if c.name == " ".join(cmd[1:])][
                            0
                        ]
                        ses.real_character = ses.character
                        ses.notify_self()
                elif (
                    "/setevent" in msg and ses.game and ses.game.deck
                ):  # add event before the position /setevent (position) 0 (name) Peyote
                    cmd = msg.split()
                    if len(cmd) >= 3:
                        sio.emit(
                            "chat_message",
                            room=ses.game.name,
                            data={
                                "color": "red",
                                "text": f"🚨 {ses.name} is in debug mode and changed event",
                            },
                        )
                        import bang.expansions.fistful_of_cards.card_events as ce
                        import bang.expansions.high_noon.card_events as ceh
                        import bang.expansions.wild_west_show.card_events as cew

                        chs = []
                        chs.extend(ce.get_all_events())
                        chs.append(ce.get_endgame_card())
                        chs.extend(ceh.get_all_events())
                        chs.append(ceh.get_endgame_card())
                        chs.extend(cew.get_all_events())
                        chs.append(cew.get_endgame_card())
                        ses.game.deck.event_cards.insert(
                            int(cmd[1]),
                            [
                                c
                                for c in chs
                                if c is not None and c.name == " ".join(cmd[2:])
                            ][0],
                        )
                        ses.game.notify_event_card()
                elif "/removecard" in msg:
                    sio.emit(
                        "chat_message",
                        room=ses.game.name,
                        data={
                            "color": "red",
                            "text": f"🚨 {ses.name} is in debug mode and removed a card",
                        },
                    )
                    cmd = msg.split()
                    if len(cmd) == 2:
                        if int(cmd[1]) < len(ses.hand):
                            ses.hand.pop(int(cmd[1]))
                        else:
                            ses.equipment.pop(int(cmd[1]) - len(ses.hand))
                        ses.notify_self()
                elif "/getcard" in msg:
                    sio.emit(
                        "chat_message",
                        room=ses.game.name,
                        data={
                            "color": "red",
                            "text": f"🚨 {ses.name} is in debug mode and got a card",
                        },
                    )
                    import bang.cards as cs

                    cmd = msg.split()
                    if len(cmd) >= 2:
                        cards = cs.get_starting_deck(ses.game.expansions)
                        card_names = " ".join(cmd[1:]).split(",")
                        for cn in card_names:
                            ses.hand.append(
                                [
                                    c
                                    for c in cards
                                    if c.name.lower() == cn.lower()
                                    or c.name[0:-1].lower() == cn.lower()
                                ][0]
                            )
                            ses.notify_self()
                elif "/equipcard" in msg:
                    sio.emit(
                        "chat_message",
                        room=ses.game.name,
                        data={
                            "color": "red",
                            "text": f"🚨 {ses.name} is in debug mode and got a card",
                        },
                    )
                    import bang.cards as cs

                    cmd = msg.split()
                    if len(cmd) >= 2:
                        cards = cs.get_starting_deck(ses.game.expansions)
                        card_names = " ".join(cmd[1:]).split(",")
                        for cn in card_names:
                            ses.equipment.append(
                                [
                                    c
                                    for c in cards
                                    if c.name.lower() == cn.lower()
                                    or c.name[0:-1].lower() == cn.lower()
                                ][0]
                            )
                            ses.notify_self()
                elif "/getset" in msg:
                    sio.emit(
                        "chat_message",
                        room=ses.game.name,
                        data={
                            "color": "red",
                            "text": f"🚨 {ses.name} is in debug mode and got a card",
                        },
                    )
                    cmd = msg.split()
                    if len(cmd) >= 2:
                        from bang.expansions import DodgeCity, TheValleyOfShadows

                        if cmd[1] == "dodgecity":
                            ses.hand = DodgeCity.get_cards()
                            ses.notify_self()
                        elif "valley" in cmd[1].lower():
                            ses.hand = TheValleyOfShadows.get_cards()
                            ses.notify_self()
                elif "/getnuggets" in msg:
                    sio.emit(
                        "chat_message",
                        room=ses.game.name,
                        data={
                            "color": "red",
                            "text": f"🚨 {ses.name} is in debug mode and got nuggets",
                        },
                    )
                    import bang.cards as cs

                    cmd = msg.split()
                    if len(cmd) == 2:
                        ses.gold_nuggets += int(cmd[1])
                        ses.notify_self()
                elif "/gameinfo" in msg:
                    sio.emit(
                        "chat_message",
                        room=sid,
                        data={
                            "color": "",
                            "text": json.dumps(
                                ses.game.__dict__,
                                default=lambda o: f"<{o.__class__.__name__}() not serializable>",
                            ),
                            "type": "json",
                        },
                    )
                elif "/deckinfo" in msg:
                    sio.emit(
                        "chat_message",
                        room=sid,
                        data={
                            "color": "",
                            "text": json.dumps(
                                ses.game.deck.__dict__,
                                default=lambda o: f"<{o.__class__.__name__}() not serializable>",
                            ),
                            "type": "json",
                        },
                    )
                elif "/trainfw" in msg:
                    ses.game.deck.move_train_forward()
                elif "/status" in msg and ses.is_admin():
                    sio.emit("mount_status", room=sid)
                elif "/meinfo" in msg:
                    sio.emit(
                        "chat_message",
                        room=sid,
                        data={
                            "color": "",
                            "text": json.dumps(
                                ses.__dict__,
                                default=lambda o: f"<{o.__class__.__name__}() not serializable>",
                            ),
                            "type": "json",
                        },
                    )
                elif "/playerinfo" in msg:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={
                                "color": "",
                                "text": json.dumps(
                                    ses.game.get_player_named(cmd[1]).__dict__,
                                    default=lambda o: f"<{o.__class__.__name__}() not serializable>",
                                ),
                                "type": "json",
                            },
                        )
                elif "/cardinfo" in msg:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        sio.emit(
                            "chat_message",
                            room=sid,
                            data={
                                "color": "",
                                "text": json.dumps(
                                    ses.hand[int(cmd[1])].__dict__,
                                    default=lambda o: f"<{o.__class__.__name__}() not serializable>",
                                ),
                                "type": "json",
                            },
                        )
                elif "/mebot" in msg:
                    ses.is_bot = not ses.is_bot
                    if ses.is_bot:
                        ses.was_player = True
                    sio.start_background_task(ses.bot_spin)
                elif "/arcadekick" in msg and ses.game.started:
                    if not any(
                        (
                            p.pending_action != PendingAction.WAIT
                            for p in ses.game.players
                        )
                    ):
                        sio.emit(
                            "chat_message",
                            room=ses.game.name,
                            data={"color": "", "text": "KICKING THE ARCADE CABINET"},
                        )
                        ses.game.next_turn()
                else:
                    sio.emit(
                        "chat_message",
                        room=sid,
                        data={"color": "", "text": f"{msg} COMMAND NOT FOUND"},
                    )
        else:
            # get a color from sid
            color = sid.encode("utf-8").hex()[0:6]
            # bg color will be slightly darker and transparent
            bg_color = f"{int(color[0:2],16)-10:02x}{int(color[2:4],16)-10:02x}{int(color[4:6],16)-10:02x}20"
            sio.emit(
                "chat_message",
                room=ses.game.name,
                data={
                    "color": f"#{color}",
                    "bgcolor": f"#{bg_color}",
                    "text": f"[{ses.name}]: {msg}",
                },
            )
            if not ses.game.is_replay:
                Metrics.send_metric(
                    "chat_message",
                    points=[1],
                    tags=[f'game:{ses.game.name.replace(" ","_")}'],
                )


"""
Sockets for the help screen
"""


@sio.event
@bang_handler
def get_cards(sid):
    import bang.cards as c

    cards = c.get_starting_deck(["dodge_city"])
    cards_dict = {ca.name: ca for ca in cards}
    sio.emit(
        "cards_info",
        room=sid,
        data=json.dumps(list(cards_dict.values()), default=lambda o: o.__dict__),
    )
    Metrics.send_metric("help_screen_viewed", points=[1])


@sio.event
@bang_handler
def get_characters(sid):
    import bang.characters as ch

    cards = ch.all_characters(
        ["dodge_city", "gold_rush", "the_valley_of_shadows", "wild_west_show"]
    )
    sio.emit(
        "characters_info",
        room=sid,
        data=json.dumps(cards, default=lambda o: o.__dict__),
    )


@sio.event
@bang_handler
def get_highnooncards(sid):
    import bang.expansions.high_noon.card_events as ceh

    chs = []
    chs.extend(ceh.get_all_events())
    chs.append(ceh.get_endgame_card())
    sio.emit(
        "highnooncards_info",
        room=sid,
        data=json.dumps(chs, default=lambda o: o.__dict__),
    )


@sio.event
@bang_handler
def get_foccards(sid):
    import bang.expansions.fistful_of_cards.card_events as ce

    chs = []
    chs.extend(ce.get_all_events())
    chs.append(ce.get_endgame_card())
    sio.emit(
        "foccards_info", room=sid, data=json.dumps(chs, default=lambda o: o.__dict__)
    )


@sio.event
@bang_handler
def get_goldrushcards(sid):
    import bang.expansions.gold_rush.shop_cards as grc

    cards = grc.get_cards()
    cards_dict = {ca.name: ca for ca in cards}
    sio.emit(
        "goldrushcards_info",
        room=sid,
        data=json.dumps(list(cards_dict.values()), default=lambda o: o.__dict__),
    )


@sio.event
@bang_handler
def get_valleyofshadowscards(sid):
    import bang.expansions.the_valley_of_shadows.cards as tvos

    cards = tvos.get_starting_deck()
    cards_dict = {ca.name: ca for ca in cards}
    sio.emit(
        "valleyofshadows_info",
        room=sid,
        data=json.dumps(list(cards_dict.values()), default=lambda o: o.__dict__),
    )


@sio.event
@bang_handler
def get_wildwestshowcards(sid):
    import bang.expansions.wild_west_show.card_events as wwce

    chs = []
    chs.extend(wwce.get_all_events())
    chs.append(wwce.get_endgame_card())
    sio.emit(
        "wwscards_info", room=sid, data=json.dumps(chs, default=lambda o: o.__dict__)
    )

@sio.event
@bang_handler
def get_trainrobberycards(sid):
    print("get_trainrobberycards")
    import bang.expansions.train_robbery.cards as trc
    import bang.expansions.train_robbery.stations as trs
    import bang.expansions.train_robbery.trains as trt

    chs = []
    chs.extend(trs.get_all_stations())
    chs.extend(trt.get_locomotives())
    chs.extend(trt.get_all_cards())
    sio.emit(
        "trainrobberycards_info", room=sid, data=json.dumps({
            "cards": chs,
            "stations": trs.get_all_stations()
        }, default=lambda o: o.__dict__)
    )

@sio.event
@bang_handler
def discord_auth(sid, data):
    res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": "1059452581027532880",
            "client_secret": os.getenv("DISCORD_SECRET", ""),
            "grant_type": "authorization_code",
            "redirect_uri": data["origin"],
            "code": data["code"],
        },
        timeout=2,
    )
    if res.status_code == 200:
        sio.emit("discord_auth_succ", room=sid, data=res.json())


def pool_metrics():
    while True:
        sio.sleep(60)
        Metrics.send_metric(
            "lobbies", points=[sum(not g.is_replay for g in games.values())]
        )
        Metrics.send_metric("online_players", points=[online_players])


class CustomProxyFix:
    def __init__(self, app):
        self.app = app
        print("init")

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if "ddproxy" in path:
            newurl = urllib.parse.unquote(
                environ["QUERY_STRING"].replace("ddforward=", "")
            )
            heads = {"X-Forwarded-For": environ["REMOTE_ADDR"]}
            for header in environ["headers_raw"]:
                heads[header[0]] = header[1]
            requests.post(
                newurl, data=environ["wsgi.input"].read(), headers=heads, timeout=4
            )
            start_response("200 OK", [])
            return [""]
        return self.app(environ, start_response)


def save_games():
    while True:
        sio.sleep(2)
        if not SAVE_LOCK:
            if not os.path.exists("save"):
                os.mkdir("save")
            with open("./save/games.pickle", "wb") as save_file:
                pickle.dump(
                    [
                        g
                        for g in games.values()
                        if g.started
                        and not g.is_replay
                        and not g.is_hidden
                        and len(g.players) > 0
                    ],
                    save_file,
                )


if __name__ == "__main__":
    if os.path.exists("./save/games.pickle"):
        try:
            with open("./save/games.pickle", "rb") as file:
                temp_g = pickle.load(file)
                games = {g.name: g for g in temp_g}
                for g in games.values():
                    g.spectators = []
                    for p in g.players:
                        if p.sid != "bot":
                            sio.start_background_task(p.disconnect)
                        else:
                            sio.start_background_task(p.bot_spin)
        except:
            pass
    sio.start_background_task(save_games)
    sio.start_background_task(pool_metrics)
    eventlet.wsgi.server(eventlet.listen(("", 5001)), CustomProxyFix(app))

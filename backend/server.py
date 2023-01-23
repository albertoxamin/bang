import os
import json
import time
import random
from typing import List
import eventlet
import socketio

from bang.game import Game
from bang.players import Player, PendingAction

import requests
from discord_webhook import DiscordWebhook
from metrics import Metrics

import sys
import traceback
sys.setrecursionlimit(10**6) # this should prevents bots from stopping

import logging
logging.basicConfig(filename='out.log', level='ERROR')
from functools import wraps
from globals import G

Metrics.init()

sio = socketio.Server(cors_allowed_origins="*")
G.sio = sio

import faulthandler

faulthandler.enable()

static_files={
        '/': {'content_type': 'text/html', 'filename': 'index.html'},
        '/game': {'content_type': 'text/html', 'filename': 'index.html'},
        '/help': {'content_type': 'text/html', 'filename': 'index.html'},
        '/status': {'content_type': 'text/html', 'filename': 'index.html'},
        # '/robots.txt': {'content_type': 'text/html', 'filename': 'robots.txt'},
        '/favicon.ico': {'filename': 'favicon.ico'},
        '/img/icons': './img/icons',
        '/manifest.json': {'filename': 'manifest.json'},
        '/css': './css',
        '/media': './media',
        '/js': './js',
    }
if "UseRobots" in os.environ and os.environ['UseRobots'].upper() == "TRUE":
    static_files['/robots.txt'] = {'content_type': 'text/html', 'filename': 'robots.txt'}

for file in [f for f in os.listdir('.') if '.js' in f or '.map' in f or '.html' in f]:
    static_files[f'/{file}'] = f'./{file}'

app = socketio.WSGIApp(sio, static_files=static_files)
games: List[Game] = []
online_players = 0
blacklist: List[str] = []

def send_to_debug(error):
    for g in games:
        if g.debug or any((p.is_admin() for p in g.players)):
            sio.emit('chat_message', room=g.name, data={'color': f'red','text':json.dumps({'ERROR':error}), 'type':'json'})

save_lock = False
def bang_handler(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        global save_lock
        save_lock = True
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            print(traceback.format_exc())
            send_to_debug(traceback.format_exc())
        save_lock = False
    return wrapper_func

def advertise_lobbies():
    sio.emit('lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players), 'locked': g.password != ''} for g in games if not g.started and len(g.players) < 10 and not g.is_hidden])
    sio.emit('spectate_lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players), 'locked': g.password != ''} for g in games if g.started and not g.is_hidden and len(g.players) > 0])
    Metrics.send_metric('lobbies', points=[sum(not g.is_replay for g in games)])
    Metrics.send_metric('online_players', points=[online_players])

@sio.event
@bang_handler
def connect(sid, environ):
    global online_players
    online_players += 1
    print('connect ', sid)
    sio.enter_room(sid, 'lobby')
    sio.emit('players', room='lobby', data=online_players)
    Metrics.send_metric('online_players', points=[online_players])

@sio.event
@bang_handler
def get_online_players(sid):
    global online_players
    sio.emit('players', room='lobby', data=online_players)

@sio.event
@bang_handler
def report(sid, text):
    print(f'New report from {sid}: {text}')
    ses: Player = sio.get_session(sid)
    data=''
    if hasattr(ses, 'game'):
        data = "\n".join(ses.game.rpc_log[:-1]).strip()
    data = data +"\n@@@\n" +text
    #print(data)
    response = requests.post("https://hastebin.com/documents", data.encode('utf-8'))
    key = json.loads(response.text).get('key')
    if "DISCORD_WEBHOOK" in os.environ and len(os.environ['DISCORD_WEBHOOK']) > 0:
        webhook = DiscordWebhook(url=os.environ['DISCORD_WEBHOOK'], content=f'New bug report, replay at https://bang.xamin.it/game?replay={key} \n Info: {text}')
        response = webhook.execute()
        sio.emit('chat_message', room=sid, data={'color': f'green','text':f'Report OK'})
    else:
        print("WARNING: DISCORD_WEBHOOK not found")
    Metrics.send_event('BUG_REPORT', event_data=text)
    print(f'New bug report, replay at https://bang.xamin.it/game?replay={key}')

@sio.event
@bang_handler
def set_username(sid, username):
    ses = sio.get_session(sid)
    if not isinstance(ses, Player):
        dt = username["discord_token"] if 'discord_token' in username else None
        sio.save_session(sid, Player(username["name"], sid, discord_token=dt))
        print(f'{sid} is now {username}')
        advertise_lobbies()
    elif ses.game is None or not ses.game.started:
        username = username["name"]
        print(f'{sid} changed username to {username}')
        prev = ses.name
        if ses.game and any((p.name == username for p in ses.game.players)):
            ses.name = f"{username}_{random.randint(0,100)}"
        else:
            ses.name = username
        sio.emit('chat_message', room=ses.game.name, data=f'_change_username|{prev}|{ses.name}')
        sio.emit('me', data=ses.name, room=sid)
        ses.game.notify_room()

@sio.event
@bang_handler
def get_me(sid, data):
    if isinstance(sio.get_session(sid), Player):
        sio.emit('me', data=sio.get_session(sid).name, room=sid)
        if sio.get_session(sid).game:
            sio.get_session(sid).game.notify_room()
    else:
        dt = data["discord_token"] if 'discord_token' in data else None
        sio.save_session(sid, Player('player', sid, discord_token=dt))
        if 'replay' in data and data['replay'] is not None:
            create_room(sid, data['replay'])
            sid = sio.get_session(sid)
            sid.game.is_hidden = True
            eventlet.sleep(0.5)
            response = requests.get(f"https://hastebin.com/raw/{data['replay']}")
            if response.status_code != 200:
                sio.emit('chat_message', room=sid, data={'color': f'green','text':f'Invalid replay code'})
                return
            log = response.text.splitlines()
            sid.game.spectators.append(sid)
            if 'ffw' not in data:
                sid.game.replay(log)
            else:
                sid.game.replay(log, speed=0, fast_forward=int(data['ffw']))
            return
        if (room := next((g for g in games if g.name == data['name']), None)) is not None:
            if not room.started:
                join_room(sid, data)
            elif room.started:
                print('room exists')
                if data['username'] is not None and any((p.name == data['username'] for p in room.players if (p.is_bot or (dt is not None and p.discord_token == dt) or p.sid is None))):
                    print('getting inside the bot')
                    bot = [p for p in room.players if (p.is_bot or (dt is not None and p.discord_token == dt) or p.sid is None) and p.name == data['username']][0]
                    bot.sid = sid
                    bot.is_bot = False
                    sio.enter_room(sid, room.name)
                    sio.save_session(sid, bot)
                    room.notify_room(sid)
                    eventlet.sleep(0.1)
                    room.notify_all()
                    room.notify_scrap_pile(sid)
                    sio.emit('role', room=sid, data=json.dumps(bot.role, default=lambda o: o.__dict__))
                    bot.notify_self()
                    if len(bot.available_characters) > 0:
                        bot.set_available_character(bot.available_characters)
                else: #spectate
                    room.spectators.append(sio.get_session(sid))
                    sio.get_session(sid).game = room
                    sio.enter_room(sid, room.name)
                    room.notify_room(sid)
                    eventlet.sleep(0.1)
                    room.notify_event_card(sid)
                    room.notify_scrap_pile(sid)
                    room.notify_all()
                room.notify_gold_rush_shop()
                room.notify_event_card()
        else:
            create_room(sid, data['name'])
        if (p := sio.get_session(sid)).game is None:
            sio.emit('me', data={'error':'Wrong password/Cannot connect'}, room=sid)
        else:
            sio.emit('me', data=p.name, room=sid)
            if data['username'] is None or any((pl.name == data['username'] for pl in p.game.players if not ((dt is not None and pl.discord_token == dt) or pl.sid is None))):
                sio.emit('change_username', room=sid)
            else:
                sio.emit('chat_message', room=p.game.name, data=f"_change_username|{p.name}|{data['username']}")
                p.name = data['username']
                sio.emit('me', data=p.name, room=sid)
                if not p.game.started:
                    p.game.notify_room()

@sio.event
@bang_handler
def disconnect(sid):
    global online_players
    online_players -= 1
    if (p := sio.get_session(sid)) is not None:
        sio.emit('players', room='lobby', data=online_players)
        if p.game and p.disconnect():
            sio.close_room(p.game.name)
            if p.game in games:
                games.pop(games.index(p.game))
        print('disconnect ', sid)
        advertise_lobbies()
    Metrics.send_metric('online_players', points=[online_players])

@sio.event
@bang_handler
def create_room(sid, room_name):
    if (p := sio.get_session(sid)).game is None:
        while any((g.name == room_name for g in games)):
            room_name += f'_{random.randint(0,100)}'
        sio.leave_room(sid, 'lobby')
        sio.enter_room(sid, room_name)
        g = Game(room_name)
        g.add_player(p)
        if room_name in blacklist:
            g.is_hidden = True
        games.append(g)
        print(f'{sid} created a room named {room_name}')
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
    g = sio.get_session(sid).game
    g.toggle_expansion(expansion_name)

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
    room_name = room['name']
    i = [g.name for g in games].index(room_name)
    if games[i].password != '' and games[i].password != room['password'].upper():
        return
    if not games[i].started:
        print(f'{sid} joined a room named {room_name}')
        sio.leave_room(sid, 'lobby')
        sio.enter_room(sid, room_name)
        while any((p.name == sio.get_session(sid).name and not p.is_bot for p in games[i].players)):
            sio.get_session(sid).name += f'_{random.randint(0,100)}'
        sio.emit('me', data=sio.get_session(sid).name, room=sid)
        games[i].add_player(sio.get_session(sid))
        advertise_lobbies()
    else:
        games[i].spectators.append(sio.get_session(sid))
        sio.get_session(sid).game = games[i]
        sio.get_session(sid).pending_action = PendingAction.WAIT
        sio.enter_room(sid, games[0].name)
        games[i].notify_room(sid)
        eventlet.sleep(0.5)
        games[i].notify_room(sid)
        games[i].notify_all()

"""
Sockets for the status page
"""

@sio.event
@bang_handler
def get_all_rooms(sid, deploy_key):
    ses = sio.get_session(sid)
    if ('DEPLOY_KEY' in os.environ and deploy_key == os.environ['DEPLOY_KEY']) or (isinstance(ses, Player) and ses.is_admin()):
        sio.emit('all_rooms', room=sid, data=[{
            'name': g.name,
            'hidden': g.is_hidden,
            'players': [{'name':p.name, 'bot': p.is_bot, 'health': p.lives, 'sid': p.sid} for p in g.players],
            'password': g.password,
            'expansions': g.expansions,
            'started': g.started,
            'current_turn': g.turn,
            'incremental_turn': g.incremental_turn,
            'debug': g.debug,
            'spectators': len(g.spectators)
        } for g in games])

@sio.event
@bang_handler
def kick(sid, data):
    ses = sio.get_session(sid)
    if ('DEPLOY_KEY' in os.environ and 'key' in data and data['key'] == os.environ['DEPLOY_KEY']) or (isinstance(ses, Player) and ses.is_admin()):
        sio.emit('kicked', room=data['sid'])

@sio.event
@bang_handler
def reset(sid, data):
    global games
    ses = sio.get_session(sid)
    if ('DEPLOY_KEY' in os.environ and 'key' in data and data['key'] == os.environ['DEPLOY_KEY']) or (isinstance(ses, Player) and ses.is_admin()):
        for g in games:
            sio.emit('kicked', room=g.name)
        games = []

@sio.event
@bang_handler
def hide_toogle(sid, data):
    ses = sio.get_session(sid)
    if ('DEPLOY_KEY' in os.environ and 'key' in data and data['key'] == os.environ['DEPLOY_KEY']) or (isinstance(ses, Player) and ses.is_admin()):
        game = [g for g in games if g.name==data['room']]
        if len(games) > 0:
            game[0].is_hidden = not game[0].is_hidden
            if game[0].is_hidden:
                if not data['room'] in blacklist:
                    blacklist.append(data['room'])
            elif data['room'] in blacklist:
                blacklist.remove(data['room'])
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
    ses.game.rpc_log.append(f'{ses.name};set_character;{name}')
    if not ses.game.is_replay:
        Metrics.send_metric('set_character', points=[1], tags=[f"char:{name}"])
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
    ses.game.rpc_log.append(f'{ses.name};draw;{pile}')
    ses.draw(pile)

@sio.event
@bang_handler
def pick(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};pick')
    ses.pick()

@sio.event
@bang_handler
def end_turn(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};end_turn')
    ses.end_turn()

@sio.event
@bang_handler
def play_card(sid, data):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};play_card;{json.dumps(data)}')
    ses.play_card(data['index'], data['against'], data['with'])

@sio.event
@bang_handler
def respond(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};respond;{card_index}')
    ses.respond(card_index)

@sio.event
@bang_handler
def choose(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};choose;{card_index}')
    ses.choose(card_index)

@sio.event
@bang_handler
def scrap(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};scrap;{card_index}')
    ses.scrap(card_index)

@sio.event
def special(sid, data):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};special;{json.dumps(data)}')
    ses.special(data)

@sio.event
@bang_handler
def gold_rush_discard(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};gold_rush_discard;')
    ses.gold_rush_discard()

@sio.event
@bang_handler
def buy_gold_rush_card(sid, data:int):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};buy_gold_rush_card;{data}')
    ses.buy_gold_rush_card(data)

@sio.event
@bang_handler
def chat_message(sid, msg, pl=None):
    ses: Player = sio.get_session(sid) if pl is None else pl
    ses.game.rpc_log.append(f'{ses.name};chat_message;{msg}')
    if len(msg) > 0:
        if msg[0] == '/':
            commands = msg.split(';')
            for msg in commands:
                if '/addbot' in msg and not ses.game.started:
                    if len(msg.split()) > 1:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'Only 1 bot at the time'})
                    else:
                        bot = Player(f'AI_{random.randint(0,10)}', 'bot', bot=True)
                        while any((p for p in ses.game.players if p.name == bot.name)):
                            bot = Player(f'AI_{random.randint(0,10)}', 'bot', bot=True)
                        ses.game.add_player(bot)
                        sio.start_background_task(bot.bot_spin)
                    return
                if '/replay' in msg and not '/replayspeed' in msg and not '/replaypov' in msg:
                    _cmd = msg.split()
                    if len(_cmd) >= 2:
                        replay_id = _cmd[1]
                        response = requests.get(f"https://hastebin.com/raw/{replay_id}")
                        log = response.text.splitlines()
                        ses.game.spectators.append(ses)
                        if len(_cmd) == 2:
                            ses.game.replay(log)
                        if len(_cmd) == 3:
                            line = int(_cmd[2])
                            ses.game.replay(log, speed=0, fast_forward=line)
                    return
                if '/replayspeed' in msg:
                    _cmd = msg.split()
                    if len(_cmd) == 2:
                        ses.game.replay_speed = float(_cmd[1])
                    return
                if '/replaypov' in msg:
                    _cmd = msg.split()
                    if len(_cmd) > 1:
                        name = ' '.join(_cmd[1:])
                        for p in ses.game.players:
                            if p.sid == ses.sid:
                                p.sid = ''
                        pl = ses.game.get_player_named(name)
                        pl.sid = ses.sid
                        pl.set_role(pl.role)
                        pl.notify_self()
                    return
                if '/startwithseed' in msg and not ses.game.started:
                    if len(msg.split()) > 1:
                        ses.game.start_game(int(msg.split()[1]))
                    return
                elif '/removebot' in msg and not ses.game.started:
                    if any((p.is_bot for p in ses.game.players)):
                        [p for p in ses.game.players if p.is_bot][-1].disconnect()
                    return
                elif '/togglecomp' in msg and ses.game:
                    ses.game.toggle_competitive()
                    return
                if '/debug' in msg:
                    cmd = msg.split()
                    if len(cmd) == 2 and 'DEPLOY_KEY' in os.environ and cmd[1] == os.environ['DEPLOY_KEY']:  # solo chi ha la deploy key può attivare la modalità debug
                        ses.game.debug = not ses.game.debug
                        ses.game.notify_room()
                    elif ses == ses.game.players[0] or ses.is_admin(): # solo l'owner può attivare la modalità debug
                        ses.game.debug = not ses.game.debug
                        ses.game.notify_room()
                    if ses.game.debug:
                        sio.emit('chat_message', room=sid, data={'color': f'red','text':f'debug mode is now active, only the owner of the room can disable it with /debug'})
                    return
                if not ses.game.debug and not ses.is_admin():
                    sio.emit('chat_message', room=sid, data={'color': f'','text':f'debug mode is not active, only the owner of the room can enable it with /debug'})
                elif '/set_chars' in msg and not ses.game.started:
                    cmd = msg.split()
                    if len(cmd) == 2 and int(cmd[1]) > 0:
                        ses.game.characters_to_distribute = int(cmd[1])
                elif '/suicide' in msg and ses.game.started and ses.lives > 0:
                    ses.lives = 0
                    ses.notify_self()
                elif '/nextevent' in msg and ses.game.started:
                    ses.game.deck.flip_event()
                elif '/notify' in msg and ses.game.started:
                    cmd = msg.split()
                    if len(cmd) >= 3:
                        if cmd[1] in ses.game.players_map:
                            ses.game.get_player_named(cmd[1]).notify_card(ses, {
                                'name': ' '.join(cmd[2:]),
                                'icon': '🚨',
                                'suit': 4,
                                'number': ' '.join(cmd[2:])
                            })
                    else:
                        sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} bad format'})
                elif '/show_cards' in msg and ses.game.started:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        if cmd[1] in ses.game.players_map:
                            sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and is looking at {cmd[1]} hand'})
                            for c in ses.game.get_player_named(cmd[1]).hand:
                                ses.notify_card(ses, c)
                                eventlet.sleep(0.3)
                    else:
                        sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} bad format'})
                elif '/ddc' in msg and ses.game.started: # debug destroy cards usage: [/ddc *] [/ddc username]
                    cmd = msg.split() 
                    if len(cmd) == 2:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode destroyed {cmd[1]} cards'})
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
                        sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} bad format'})
                elif '/dsh' in msg and ses.game.started: #debug set health usage [/dsh * hp] [/dsh username hp]
                    cmd = msg.split()
                    if len(cmd) == 3:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and is changing {cmd[1]} health'})
                        if cmd[1] == "*":
                            for p in ses.game.players_map:
                                ses.game.get_player_named(p).lives = min(int(cmd[2]), ses.game.get_player_named(p).max_lives)
                                ses.game.get_player_named(p).notify_self()
                        elif cmd[1] in ses.game.players_map:
                            ses.game.get_player_named(cmd[1]).lives = min(int(cmd[2]), ses.game.get_player_named(cmd[1]).max_lives)
                            ses.game.get_player_named(cmd[1]).notify_self()
                    else:
                        sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} bad format'})
                elif '/togglebot' in msg and ses.game:
                    ses.game.toggle_disconnect_bot()
                elif '/cancelgame' in msg and ses.game.started:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} stopped the current game'})
                    ses.game.reset()
                elif '/startgame' in msg and not ses.game.started:
                    ses.game.start_game()
                elif '/setbotspeed' in msg:
                    ses.game.bot_speed = float(msg.split()[1])
                elif '/addex' in msg and not ses.game.started:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        cmd[1] = cmd[1].replace('foc', 'fistful_of_cards')
                        if cmd[1] not in ses.game.available_expansions:
                            ses.game.available_expansions.append(cmd[1])
                            ses.game.notify_room()
                    else:
                        sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} bad format'})
                elif '/setcharacter' in msg:
                    import bang.characters as characters
                    cmd = msg.split()
                    if len(cmd) >= 2:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and changed character'})
                        chs = characters.all_characters(ses.game.expansions)
                        ses.character = [c for c in chs if c.name == ' '.join(cmd[1:])][0]
                        ses.real_character = ses.character
                        ses.notify_self()
                elif '/setevent' in msg and ses.game and ses.game.deck: #add event before the position /setevent (position) 0 (name) Peyote
                    cmd = msg.split()
                    if len(cmd) >= 3:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and changed event'})
                        import bang.expansions.fistful_of_cards.card_events as ce
                        import bang.expansions.high_noon.card_events as ceh
                        chs = []
                        chs.extend(ce.get_all_events())
                        chs.append(ce.get_endgame_card())
                        chs.extend(ceh.get_all_events())
                        chs.append(ceh.get_endgame_card())
                        ses.game.deck.event_cards.insert(int(cmd[1]), [c for c in chs if c is not None and c.name == ' '.join(cmd[2:])][0])
                        ses.game.notify_event_card()
                elif '/removecard' in msg:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and removed a card'})
                    cmd = msg.split()
                    if len(cmd) == 2:
                        if int(cmd[1]) < len(ses.hand):
                            ses.hand.pop(int(cmd[1]))
                        else:
                            ses.equipment.pop(int(cmd[1])-len(ses.hand))
                        ses.notify_self()
                elif '/getcard' in msg:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and got a card'})
                    import bang.cards as cs
                    cmd = msg.split()
                    if len(cmd) >= 2:
                        cards  = cs.get_starting_deck(ses.game.expansions)
                        card_names = ' '.join(cmd[1:]).split(',')
                        for cn in card_names:
                            ses.hand.append([c for c in cards if c.name.lower() == cn.lower() or c.name[0:-1].lower() == cn.lower()][0])
                            ses.notify_self()
                elif '/equipcard' in msg:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and got a card'})
                    import bang.cards as cs
                    cmd = msg.split()
                    if len(cmd) >= 2:
                        cards  = cs.get_starting_deck(ses.game.expansions)
                        card_names = ' '.join(cmd[1:]).split(',')
                        for cn in card_names:
                            ses.equipment.append([c for c in cards if c.name.lower() == cn.lower() or c.name[0:-1].lower() == cn.lower()][0])
                            ses.notify_self()
                elif '/getset' in msg:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and got a card'})
                    cmd = msg.split()
                    if len(cmd) >= 2:
                        from bang.expansions import DodgeCity, TheValleyOfShadows
                        if cmd[1] == 'dodgecity':
                            ses.hand = DodgeCity.get_cards()
                            ses.notify_self()
                        elif 'valley' in cmd[1].lower():
                            ses.hand = TheValleyOfShadows.get_cards()
                            ses.notify_self()
                elif '/getnuggets' in msg:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and got nuggets'})
                    import bang.cards as cs
                    cmd = msg.split()
                    if len(cmd) == 2:
                        ses.gold_nuggets += int(cmd[1])
                        ses.notify_self()
                elif '/gameinfo' in msg:
                    sio.emit('chat_message', room=sid, data={'color': f'', 'text':json.dumps(ses.game.__dict__, default=lambda o: f'<{o.__class__.__name__}() not serializable>'), 'type': 'json'})
                elif '/status' in msg and ses.is_admin():
                    sio.emit('mount_status', room=sid)
                elif '/meinfo' in msg:
                    sio.emit('chat_message', room=sid, data={'color': f'', 'text':json.dumps(ses.__dict__, default=lambda o: f'<{o.__class__.__name__}() not serializable>'), 'type': 'json'})
                elif '/playerinfo' in msg:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        sio.emit('chat_message', room=sid, data={'color': f'', 'text':json.dumps(ses.game.get_player_named(cmd[1]).__dict__, default=lambda o: f'<{o.__class__.__name__}() not serializable>'), 'type': 'json'})
                elif '/cardinfo' in msg:
                    cmd = msg.split()
                    if len(cmd) == 2:
                        sio.emit('chat_message', room=sid, data={'color': f'', 'text':json.dumps(ses.hand[int(cmd[1])].__dict__, default=lambda o: f'<{o.__class__.__name__}() not serializable>'), 'type': 'json'})
                elif '/mebot' in msg:
                    ses.is_bot = not ses.is_bot
                    if (ses.is_bot):
                        ses.was_player = True
                    sio.start_background_task(ses.bot_spin)
                elif '/arcadekick' in msg and ses.game.started:
                    if not any((p.pending_action != PendingAction.WAIT for p in ses.game.players)):
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'','text':f'KICKING THE ARCADE CABINET'})
                        ses.game.next_turn()
                else:
                    sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} COMMAND NOT FOUND'})
        else:
            # get a color from sid
            color = sid.encode('utf-8').hex()[0:6]
            #bg color will be slightly darker and transparent
            bg_color = f'{int(color[0:2],16)-10:02x}{int(color[2:4],16)-10:02x}{int(color[4:6],16)-10:02x}20'
            sio.emit('chat_message', room=ses.game.name, data={'color': f'#{color}', 'bgcolor': f'#{bg_color}','text':f'[{ses.name}]: {msg}'})
            if not ses.game.is_replay:
                Metrics.send_metric('chat_message', points=[1], tags=[f'game:{ses.game.name.replace(" ","_")}'])



"""
Sockets for the help screen
"""

@sio.event
@bang_handler
def get_cards(sid):
    import bang.cards as c
    cards = c.get_starting_deck(['dodge_city'])
    cards_dict = {}
    for ca in cards:
        if ca.name not in cards_dict:
            cards_dict[ca.name] = ca
    cards = [cards_dict[i] for i in cards_dict]
    sio.emit('cards_info', room=sid, data=json.dumps(cards, default=lambda o: o.__dict__))
    Metrics.send_metric('help_screen_viewed', points=[1])

@sio.event
@bang_handler
def get_characters(sid):
    import bang.characters as ch
    cards = ch.all_characters(['dodge_city', 'gold_rush'])
    sio.emit('characters_info', room=sid, data=json.dumps(cards, default=lambda o: o.__dict__))

@sio.event
@bang_handler
def get_highnooncards(sid):
    import bang.expansions.high_noon.card_events as ceh
    chs = []
    chs.extend(ceh.get_all_events())
    chs.append(ceh.get_endgame_card())
    sio.emit('highnooncards_info', room=sid, data=json.dumps(chs, default=lambda o: o.__dict__))

@sio.event
@bang_handler
def get_foccards(sid):
    import bang.expansions.fistful_of_cards.card_events as ce
    chs = []
    chs.extend(ce.get_all_events())
    chs.append(ce.get_endgame_card())
    sio.emit('foccards_info', room=sid, data=json.dumps(chs, default=lambda o: o.__dict__))

@sio.event
@bang_handler
def get_goldrushcards(sid):
    import bang.expansions.gold_rush.shop_cards as grc
    cards = grc.get_cards()
    cards_dict = {}
    for ca in cards:
        if ca.name not in cards_dict:
            cards_dict[ca.name] = ca
    cards = [cards_dict[i] for i in cards_dict]
    sio.emit('goldrushcards_info', room=sid, data=json.dumps(cards, default=lambda o: o.__dict__))

@sio.event
@bang_handler
def get_valleyofshadowscards(sid):
    import bang.expansions.the_valley_of_shadows.cards as tvos
    cards = tvos.get_starting_deck()
    cards_dict = {}
    for ca in cards:
        if ca.name not in cards_dict:
            cards_dict[ca.name] = ca
    cards = [cards_dict[i] for i in cards_dict]
    sio.emit('valleyofshadows_info', room=sid, data=json.dumps(cards, default=lambda o: o.__dict__))

@sio.event
@bang_handler
def discord_auth(sid, data):
    res = requests.post('https://discord.com/api/oauth2/token', data={
        'client_id': '1059452581027532880',
        'client_secret': 'Mc8ZlMQhayzi1eOqWFtGHs3L0iXCzaEu',
        'grant_type': 'authorization_code',
        'redirect_uri': data['origin'],
        'code': data['code'],
    })
    if res.status_code == 200:
        sio.emit('discord_auth_succ', room=sid, data=res.json())


def pool_metrics():
    while True:
        sio.sleep(60)
        Metrics.send_metric('lobbies', points=[sum(not g.is_replay for g in games)])
        Metrics.send_metric('online_players', points=[online_players])

import urllib.parse
class CustomProxyFix(object):
    def __init__(self, app):
        self.app = app
        print('init')

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if 'ddproxy' in path:
            newurl = urllib.parse.unquote(environ['QUERY_STRING'].replace('ddforward=', ''))
            heads = {'X-Forwarded-For': environ['REMOTE_ADDR']}
            for h in environ['headers_raw']:
                heads[h[0]] = h[1]
            r = requests.post(newurl, data=environ['wsgi.input'].read(), headers=heads)
            start_response('200 OK', [])
            return ['']
        return self.app(environ, start_response)


discord_ci = '1059452581027532880'
discord_cs = 'Mc8ZlMQhayzi1eOqWFtGHs3L0iXCzaEu'
import pickle
def save_games():
    global save_lock
    while True:
        sio.sleep(2)
        if not save_lock:
            if not os.path.exists("save"):
                os.mkdir("save")
            with open('./save/games.pickle', 'wb') as f:
                pickle.dump([g for g in games if g.started and not g.is_replay and not g.is_hidden], f)

if __name__ == '__main__':
    if os.path.exists('./save/games.pickle'):
        try:
            with open('./save/games.pickle', 'rb') as file:
                games = pickle.load(file)
                for g in games:
                    g.spectators = []
                    for p in g.players:
                        if p.sid != 'bot':
                            sio.start_background_task(p.disconnect)
                        else:
                            sio.start_background_task(p.bot_spin)
        except:
            pass
    sio.start_background_task(save_games)
    sio.start_background_task(pool_metrics)
    eventlet.wsgi.server(eventlet.listen(('', 5001)), CustomProxyFix(app))

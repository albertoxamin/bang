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


Metrics.init()

import sys 
sys.setrecursionlimit(10**6) # this should prevents bots from stopping

sio = socketio.Server(cors_allowed_origins="*")

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

def advertise_lobbies():
    sio.emit('lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players), 'locked': g.password != ''} for g in games if not g.started and len(g.players) < 10 and not g.is_hidden])
    sio.emit('spectate_lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players), 'locked': g.password != ''} for g in games if g.started])
    Metrics.send_metric('lobbies', points=[len(games)])
    Metrics.send_metric('online_players', points=[online_players])

@sio.event
def connect(sid, environ):
    global online_players
    online_players += 1
    print('connect ', sid)
    sio.enter_room(sid, 'lobby')
    sio.emit('players', room='lobby', data=online_players)
    Metrics.send_metric('online_players', points=[online_players])

@sio.event
def get_online_players(sid):
    global online_players
    sio.emit('players', room='lobby', data=online_players)

@sio.event
def report(sid, text):
    ses: Player = sio.get_session(sid)
    data=''
    if hasattr(ses, 'game'):
        data = "\n".join(ses.game.rpc_log[:-1]).strip()
    data = data +"\n@@@\n" +text
    #print(data)
    response = requests.post("https://www.toptal.com/developers/hastebin/documents", data)
    key = json.loads(response.text).get('key')
    if "DISCORD_WEBHOOK" in os.environ and len(os.environ['DISCORD_WEBHOOK']) > 0:
        webhook = DiscordWebhook(url=os.environ['DISCORD_WEBHOOK'], content=f'New bug report, replay at https://www.toptal.com/developers/hastebin/{key}')
        response = webhook.execute()
        sio.emit('chat_message', room=sid, data={'color': f'green','text':f'Report OK'})
    else:
        print("WARNING: DISCORD_WEBHOOK not found")
    Metrics.send_event('BUG_REPORT', event_data=text)
    print(f'New bug report, replay at https://www.toptal.com/developers/hastebin/{key}')

@sio.event
def set_username(sid, username):
    ses = sio.get_session(sid)
    if not isinstance(ses, Player):
        sio.save_session(sid, Player(username, sid, sio))
        print(f'{sid} is now {username}')
        advertise_lobbies()
    elif ses.game == None or not ses.game.started:
        print(f'{sid} changed username to {username}')
        prev = ses.name
        if len([p for p in ses.game.players if p.name == username]) > 0:
            ses.name = f"{username}_{random.randint(0,100)}"
        else:
            ses.name = username
        sio.emit('chat_message', room=ses.game.name, data=f'_change_username|{prev}|{ses.name}')
        sio.emit('me', data=ses.name, room=sid)
        ses.game.notify_room()

@sio.event
def get_me(sid, room):
    if isinstance(sio.get_session(sid), Player):
        sio.emit('me', data=sio.get_session(sid).name, room=sid)
        if sio.get_session(sid).game:
            sio.get_session(sid).game.notify_room()
    else:
        sio.save_session(sid, Player('player', sid, sio))
        de_games = [g for g in games if g.name == room['name']]
        if len(de_games) == 1 and not de_games[0].started:
            join_room(sid, room)
        elif len(de_games) == 1 and de_games[0].started:
            print('room exists')
            if room['username'] != None and any([p.name == room['username'] for p in de_games[0].players if p.is_bot]):
                print('getting inside the bot')
                bot = [p for p in de_games[0].players if p.is_bot and p.name == room['username'] ][0]
                bot.sid = sid
                bot.is_bot = False
                sio.enter_room(sid, de_games[0].name)
                sio.save_session(sid, bot)
                de_games[0].notify_room(sid)
                eventlet.sleep(0.1)
                de_games[0].notify_all()
                sio.emit('role', room=sid, data=json.dumps(bot.role, default=lambda o: o.__dict__))
                bot.notify_self()
                if len(bot.available_characters) > 0:
                    bot.set_available_character(bot.available_characters)
            else: #spectate
                de_games[0].spectators.append(sio.get_session(sid))
                sio.get_session(sid).game = de_games[0]
                sio.enter_room(sid, de_games[0].name)
                de_games[0].notify_room(sid)
                de_games[0].notify_event_card(sid)
                de_games[0].notify_scrap_pile(sid)
                de_games[0].notify_all()
            de_games[0].notify_gold_rush_shop()
            de_games[0].notify_event_card()
        else:
            create_room(sid, room['name'])
        if sio.get_session(sid).game == None:
            sio.emit('me', data={'error':'Wrong password/Cannot connect'}, room=sid)
        else:
            sio.emit('me', data=sio.get_session(sid).name, room=sid)
            if room['username'] == None or any([p.name == room['username'] for p in sio.get_session(sid).game.players]):
                sio.emit('change_username', room=sid)
            else:
                sio.emit('chat_message', room=sio.get_session(sid).game.name, data=f"_change_username|{sio.get_session(sid).name}|{room['username']}")
                sio.get_session(sid).name = room['username']
                sio.emit('me', data=sio.get_session(sid).name, room=sid)
                if not sio.get_session(sid).game.started:
                    sio.get_session(sid).game.notify_room()

@sio.event
def disconnect(sid):
    global online_players
    online_players -= 1
    if sio.get_session(sid):
        sio.emit('players', room='lobby', data=online_players)
        if sio.get_session(sid).game and sio.get_session(sid).disconnect():
            sio.close_room(sio.get_session(sid).game.name)
            games.pop(games.index(sio.get_session(sid).game))
        print('disconnect ', sid)
        advertise_lobbies()
    Metrics.send_metric('online_players', points=[online_players])

@sio.event
def create_room(sid, room_name):
    if sio.get_session(sid).game == None:
        while len([g for g in games if g.name == room_name]):
            room_name += f'_{random.randint(0,100)}'
        sio.leave_room(sid, 'lobby')
        sio.enter_room(sid, room_name)
        g = Game(room_name, sio)
        g.add_player(sio.get_session(sid))
        if room_name in blacklist:
            g.is_hidden = True
        games.append(g)
        print(f'{sid} created a room named {room_name}')
        advertise_lobbies()

@sio.event
def private(sid):
    g = sio.get_session(sid).game
    g.set_private()
    advertise_lobbies()

@sio.event
def toggle_expansion(sid, expansion_name):
    g = sio.get_session(sid).game
    g.toggle_expansion(expansion_name)

@sio.event
def toggle_comp(sid):
    sio.get_session(sid).game.toggle_competitive()

@sio.event
def toggle_replace_with_bot(sid):
    sio.get_session(sid).game.toggle_disconnect_bot()

@sio.event
def join_room(sid, room):
    room_name = room['name']
    i = [g.name for g in games].index(room_name)
    if games[i].password != '' and games[i].password != room['password'].upper():
        return
    if not games[i].started:
        print(f'{sid} joined a room named {room_name}')
        sio.leave_room(sid, 'lobby')
        sio.enter_room(sid, room_name)
        while len([p for p in games[i].players if p.name == sio.get_session(sid).name]):
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
def get_all_rooms(sid, deploy_key):
    if 'DEPLOY_KEY' in os.environ and deploy_key == os.environ['DEPLOY_KEY']:
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
def kick(sid, data):
    if 'DEPLOY_KEY' in os.environ and data['key'] == os.environ['DEPLOY_KEY']:
        sio.emit('kicked', room=data['sid'])

@sio.event
def hide_toogle(sid, data):
    if 'DEPLOY_KEY' in os.environ and data['key'] == os.environ['DEPLOY_KEY']:
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
def start_game(sid):
    ses: Player = sio.get_session(sid)
    ses.game.start_game()
    advertise_lobbies()

@sio.event
def set_character(sid, name):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};set_character;{name}')
    Metrics.send_metric('set_character', points=[1], tags=[f"char:{name}"])
    ses.set_character(name)

@sio.event
def refresh(sid):
    ses: Player = sio.get_session(sid)
    ses.notify_self()

@sio.event
def draw(sid, pile):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};draw;{pile}')
    ses.draw(pile)

@sio.event
def pick(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};pick')
    ses.pick()

@sio.event
def end_turn(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};end_turn')
    ses.end_turn()

@sio.event
def play_card(sid, data):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};play_card;{json.dumps(data)}')
    ses.play_card(data['index'], data['against'], data['with'])

@sio.event
def respond(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};respond;{card_index}')
    ses.respond(card_index)

@sio.event
def choose(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};choose;{card_index}')
    ses.choose(card_index)

@sio.event
def scrap(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};scrap;{card_index}')
    ses.scrap(card_index)

@sio.event
def special(sid, data):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};play_card;{json.dumps(data)}')
    ses.special(data)

@sio.event
def gold_rush_discard(sid):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};gold_rush_discard;')
    ses.gold_rush_discard()

@sio.event
def buy_gold_rush_card(sid, data:int):
    ses: Player = sio.get_session(sid)
    ses.game.rpc_log.append(f'{ses.name};buy_gold_rush_card;{data}')
    ses.buy_gold_rush_card(data)

@sio.event
def chat_message(sid, msg, pl=None):
    ses: Player = sio.get_session(sid) if pl is None else pl
    ses.game.rpc_log.append(f'{ses.name};chat_message;{msg}')
    if len(msg) > 0:
        if msg[0] == '/':
            commands = msg.split(';')
            for msg in commands:
                if '/addbot' in msg and not ses.game.started:
                    if len(msg.split()) > 1:
                        # for _ in range(int(msg.split()[1])):
                        #     ses.game.add_player(Player(f'AI_{random.randint(0,1000)}', 'bot', sio, bot=True))
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'Only 1 bot at the time'})
                    else:
                        bot = Player(f'AI_{random.randint(0,10)}', 'bot', sio, bot=True)
                        while any([p for p in ses.game.players if p.name == bot.name]):
                            bot = Player(f'AI_{random.randint(0,10)}', 'bot', sio, bot=True)
                        ses.game.add_player(bot)
                        bot.bot_spin()
                    return
                if '/replay' in msg and not '/replayspeed' in msg:
                    _cmd = msg.split()
                    if len(_cmd) == 2:
                        replay_id = _cmd[1]
                        response = requests.get(f"https://www.toptal.com/developers/hastebin/raw/{replay_id}")
                        log = response.text.splitlines()
                        ses.game.spectators.append(ses)
                        ses.game.replay(log)
                    return
                if '/replayspeed' in msg:
                    _cmd = msg.split()
                    if len(_cmd) == 2:
                        ses.game.replay_speed = float(_cmd[1])
                    return
                if '/startwithseed' in msg and not ses.game.started:
                    if len(msg.split()) > 1:
                        ses.game.start_game(int(msg.split()[1]))
                    return
                elif '/removebot' in msg and not ses.game.started:
                    if any([p.is_bot for p in ses.game.players]):
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
                    elif ses == ses.game.players[0]: # solo l'owner può attivare la modalità debug
                        ses.game.debug = not ses.game.debug
                        ses.game.notify_room()
                    if ses.game.debug:
                        sio.emit('chat_message', room=sid, data={'color': f'red','text':f'debug mode is now active, only the owner of the room can disable it with /debug'})
                    return
                if not ses.game.debug:
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
                        ses.game.deck.event_cards.insert(int(cmd[1]), [c for c in chs if c!=None and c.name == ' '.join(cmd[2:])][0])
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
                            ses.hand.append([c for c in cards if c.name == cn][0])
                            ses.notify_self()
                elif '/getnuggets' in msg:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and got nuggets'})
                    import bang.cards as cs
                    cmd = msg.split()
                    if len(cmd) == 2:
                        ses.gold_nuggets += int(cmd[1])
                        ses.notify_self()
                elif '/gameinfo' in msg:
                    sio.emit('chat_message', room=sid, data={'color': f'','text':f'info: {dict(filter(lambda x:x[0] != "rpc_log",ses.game.__dict__.items()))}'})
                elif '/meinfo' in msg:
                    sio.emit('chat_message', room=sid, data={'color': f'','text':f'info: {ses.__dict__}'})
                elif '/mebot' in msg:
                    ses.is_bot = not ses.is_bot
                    if (ses.is_bot):
                        ses.was_player = True
                    ses.bot_spin()
                elif '/arcadekick' in msg and ses.game.started:
                    if len([p for p in ses.game.players if p.pending_action != PendingAction.WAIT]) == 0:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'','text':f'KICKING THE ARCADE CABINET'})
                        ses.game.next_turn()
                else:
                    sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} COMMAND NOT FOUND'})
        else:
            color = sid.encode('utf-8').hex()[-3:]
            sio.emit('chat_message', room=ses.game.name, data={'color': f'#{color}','text':f'[{ses.name}]: {msg}'})
            Metrics.send_metric('chat_message', points=[1], tags=[f'game:{ses.game.name.replace(" ","_")}'])



"""
Sockets for the help screen
"""

@sio.event
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
def get_characters(sid):
    import bang.characters as ch
    cards = ch.all_characters(['dodge_city', 'gold_rush'])
    sio.emit('characters_info', room=sid, data=json.dumps(cards, default=lambda o: o.__dict__))

@sio.event
def get_highnooncards(sid):
    import bang.expansions.high_noon.card_events as ceh
    chs = []
    chs.extend(ceh.get_all_events())
    chs.append(ceh.get_endgame_card())
    sio.emit('highnooncards_info', room=sid, data=json.dumps(chs, default=lambda o: o.__dict__))

@sio.event
def get_foccards(sid):
    import bang.expansions.fistful_of_cards.card_events as ce
    chs = []
    chs.extend(ce.get_all_events())
    chs.append(ce.get_endgame_card())
    sio.emit('foccards_info', room=sid, data=json.dumps(chs, default=lambda o: o.__dict__))

@sio.event
def get_goldrushcards(sid):
    import bang.expansions.gold_rush.shop_cards as grc
    cards = grc.get_cards()
    cards_dict = {}
    for ca in cards:
        if ca.name not in cards_dict:
            cards_dict[ca.name] = ca
    cards = [cards_dict[i] for i in cards_dict]
    sio.emit('goldrushcards_info', room=sid, data=json.dumps(cards, default=lambda o: o.__dict__))

def pool_metrics():
    sio.sleep(60)
    Metrics.send_metric('lobbies', points=[len(games)])
    Metrics.send_metric('online_players', points=[online_players])
    pool_metrics()

if __name__ == '__main__':
    sio.start_background_task(pool_metrics)
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

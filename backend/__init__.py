import os
import json
import random
from typing import List
import eventlet
import socketio

from bang.game import Game
from bang.players import Player, PendingAction

import sys 
sys.setrecursionlimit(10**6) # this should prevents bots from stopping

sio = socketio.Server(cors_allowed_origins="*")
static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'},
    '/game': {'content_type': 'text/html', 'filename': 'index.html'},
    # '/robots.txt': {'content_type': 'text/html', 'filename': 'robots.txt'},
    '/favicon.ico': {'filename': 'favicon.ico'},
    '/img/icons': './img/icons',
    '/manifest.json': {'filename': 'manifest.json'},
    '/css': './css',
    '/js': './js',
}
for file in [f for f in os.listdir('.') if '.js' in f or '.map' in f or '.html' in f]:
    static_files[f'/{file}'] = f'./{file}'

app = socketio.WSGIApp(sio, static_files=static_files)
games: List[Game] = []
online_players = 0

def advertise_lobbies():
    sio.emit('lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players), 'locked': g.password != ''} for g in games if not g.started and len(g.players) < 10])

@sio.event
def connect(sid, environ):
    global online_players
    online_players += 1
    print('connect ', sid)
    sio.enter_room(sid, 'lobby')
    sio.emit('players', room='lobby', data=online_players)

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
                de_games[0].notify_all()
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

@sio.event
def create_room(sid, room_name):
    if sio.get_session(sid).game == None:
        while len([g for g in games if g.name == room_name]):
            room_name += f'_{random.randint(0,100)}'
        sio.leave_room(sid, 'lobby')
        sio.enter_room(sid, room_name)
        g = Game(room_name, sio)
        g.add_player(sio.get_session(sid))
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
    print(f'{sid} joined a room named {room_name}')
    i = [g.name for g in games].index(room_name)
    if games[i].password != '' and games[i].password != room['password'].upper():
        return
    sio.leave_room(sid, 'lobby')
    sio.enter_room(sid, room_name)
    while len([p for p in games[i].players if p.name == sio.get_session(sid).name]):
        sio.get_session(sid).name += f'_{random.randint(0,100)}'
    sio.emit('me', data=sio.get_session(sid).name, room=sid)
    games[i].add_player(sio.get_session(sid))
    advertise_lobbies()

@sio.event
def chat_message(sid, msg):
    ses: Player = sio.get_session(sid)
    if len(msg) > 0:
        if msg[0] == '/':
            if '/addbot' in msg and not ses.game.started:
                if len(msg.split()) > 1:
                    # for _ in range(int(msg.split()[1])):
                    #     ses.game.add_player(Player(f'AI_{random.randint(0,1000)}', 'bot', sio, bot=True))
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'Only 1 bot at the time'})
                else:
                    bot = Player(f'AI_{random.randint(0,1000)}', 'bot', sio, bot=True)
                    ses.game.add_player(bot)
                    bot.bot_spin()
            elif '/removebot' in msg and not ses.game.started:
                if any([p.is_bot for p in ses.game.players]):
                    [p for p in ses.game.players if p.is_bot][-1].disconnect()
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
            elif '/debug_show_cards' in msg and ses.game.started:
                cmd = msg.split()
                if len(cmd) == 2:
                    if cmd[1] in ses.game.players_map:
                        sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and is looking at {cmd[1]} hand'})
                        for c in ses.game.get_player_named(cmd[1]).hand:
                            ses.notify_card(ses, c)
                            eventlet.sleep(0.3)
                else:
                    sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} bad format'})
            elif '/togglecomp' in msg and ses.game:
                ses.game.toggle_competitive()
            elif '/togglebot' in msg and ses.game:
                ses.game.toggle_disconnect_bot()
            elif '/cancelgame' in msg and ses.game.started:
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
                sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and changed character'})
                import bang.characters as characters
                cmd = msg.split()
                if len(cmd) >= 2:
                    chs = characters.all_characters(ses.game.expansions)
                    ses.character = [c for c in chs if c.name == ' '.join(cmd[1:])][0]
                    ses.real_character = ses.character
                    ses.notify_self()
            elif '/setevent' in msg and ses.game and ses.game.deck:
                cmd = msg.split()
                if len(cmd) >= 3:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'red','text':f'🚨 {ses.name} is in debug mode and changed event'})
                    chs = ses.game.deck.event_cards
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
            elif '/gameinfo' in msg:
                sio.emit('chat_message', room=sid, data={'color': f'','text':f'info: {ses.game.__dict__}'})
            elif '/meinfo' in msg:
                sio.emit('chat_message', room=sid, data={'color': f'','text':f'info: {ses.__dict__}'})
            elif '/mebot' in msg:
                ses.is_bot = not ses.is_bot
                ses.bot_spin()
            elif '/arcadekick' in msg and ses.game.started:
                if len([p for p in ses.game.players if p.pending_action != PendingAction.WAIT]) == 0:
                    sio.emit('chat_message', room=ses.game.name, data={'color': f'','text':f'KICKING THE ARCADE CABINET'})
                    ses.game.play_turn()
            else:
                sio.emit('chat_message', room=sid, data={'color': f'','text':f'{msg} COMMAND NOT FOUND'})
        else:
            color = sid.encode('utf-8').hex()[-3:]
            sio.emit('chat_message', room=ses.game.name, data={'color': f'#{color}','text':f'[{ses.name}]: {msg}'})

@sio.event
def start_game(sid):
    ses: Player = sio.get_session(sid)
    ses.game.start_game()
    advertise_lobbies()

@sio.event
def set_character(sid, name):
    ses: Player = sio.get_session(sid)
    ses.set_character(name)

@sio.event
def refresh(sid):
    ses: Player = sio.get_session(sid)
    ses.notify_self()

@sio.event
def draw(sid, pile):
    ses: Player = sio.get_session(sid)
    ses.draw(pile)

@sio.event
def pick(sid):
    ses: Player = sio.get_session(sid)
    ses.pick()

@sio.event
def end_turn(sid):
    ses: Player = sio.get_session(sid)
    ses.end_turn()

@sio.event
def play_card(sid, data):
    ses: Player = sio.get_session(sid)
    ses.play_card(data['index'], data['against'], data['with'])

@sio.event
def respond(sid, data):
    ses: Player = sio.get_session(sid)
    ses.respond(data)

@sio.event
def choose(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.choose(card_index)

@sio.event
def scrap(sid, card_index):
    ses: Player = sio.get_session(sid)
    ses.scrap(card_index)

@sio.event
def chuck_lose_hp_draw(sid):
    ses: Player = sio.get_session(sid)
    ses.chuck_lose_hp_draw()

@sio.event
def holyday_special(sid, data):
    ses: Player = sio.get_session(sid)
    ses.holyday_special(data)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

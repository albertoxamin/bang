import json
import random
from typing import List
import eventlet
import socketio

from bang.game import Game
from bang.players import Player

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'},
    '/game': {'content_type': 'text/html', 'filename': 'index.html'},
    '/favicon.ico': {'filename': 'favicon.ico'},
    '/img/icons': './img/icons',
    '/manifest.json': {'filename': 'manifest.json'},
    '/css': './css',
    '/js': './js',
})

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
    if not isinstance(sio.get_session(sid), Player):
        sio.save_session(sid, Player(username, sid, sio))
        print(f'{sid} is now {username}')
        advertise_lobbies()
    elif sio.get_session(sid).game == None or not sio.get_session(sid).game.started:
        print(f'{sid} changed username to {username}')
        if len([p for p in sio.get_session(sid).game.players if p.name == username]) > 0:
            sio.get_session(sid).name = f'{username}_{random.randint(0,100)}'
        else:
            sio.get_session(sid).name = username
        sio.emit('me', data=sio.get_session(sid).name, room=sid)
        sio.get_session(sid).game.notify_room()

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
        else:
            create_room(sid, room['name'])
        if sio.get_session(sid).game == None:
            sio.emit('me', data={'error':'Wrong password/Cannot connect'}, room=sid)
        else:
            sio.emit('me', data=sio.get_session(sid).name, room=sid)
            sio.emit('change_username', room=sid)

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
                    for _ in range(int(msg.split()[1])):
                        ses.game.add_player(Player(f'AI_{random.randint(0,100)}', 'bot', sio, bot=True))
                else:
                    ses.game.add_player(Player(f'AI_{random.randint(0,100)}', 'bot', sio, bot=True))
            elif '/removebot' in msg and not ses.game.started:
                if any([p.is_bot for p in ses.game.players]):
                    [p for p in ses.game.players if p.is_bot][-1].disconnect()
            elif '/suicide' in msg and ses.game.started:
                ses.lives = 0
                ses.notify_self()
            elif '/cancelgame' in msg and ses.game.started:
                ses.game.reset()
            elif '/gameinfo' in msg:
                sio.emit('chat_message', room=sid, data=f'info: {ses.game.__dict__}')
            elif '/meinfo' in msg:
                sio.emit('chat_message', room=sid, data=f'info: {ses.__dict__}')
            else:
                sio.emit('chat_message', room=sid, data=f'{msg} COMMAND NOT FOUND')
        else:
            sio.emit('chat_message', room=ses.game.name, data=f'[{ses.name}]: {msg}')

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

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

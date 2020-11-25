import json
import random
from typing import List
import eventlet
import socketio

from game import Game
from players import Player

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'},
    '/favicon.ico': {'filename': 'favicon.ico'},
    '/css': './css',
    '/js': './js',
})

games: List[Game] = []
online_players = 0

def advertise_lobbies():
    sio.emit('lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players), 'locked': g.password != ''} for g in games if not g.started and len(g.players) < 7])

@sio.event
def connect(sid, environ):
    print('connect ', sid)
    sio.enter_room(sid, 'lobby')
    sio.emit('players', room='lobby', data=online_players)

@sio.event
def set_username(sid, username):
    global online_players
    online_players += 1
    sio.save_session(sid, Player(username, sid, sio))
    print(f'{sid} is now {username}')
    advertise_lobbies()

@sio.event
def my_message(sid, data):
    print('message ', data)

@sio.event
def disconnect(sid):
    global online_players
    if sio.get_session(sid):
        online_players -= 1
        sio.emit('players', room='lobby', data=online_players)
        if sio.get_session(sid).game and sio.get_session(sid).disconnect():
            sio.close_room(sio.get_session(sid).game.name)
            games.pop(games.index(sio.get_session(sid).game))
        print('disconnect ', sid)
        advertise_lobbies()

@sio.event
def create_room(sid, room_name):
    while len([g for g in games if g.name == room_name]):
        room_name += '_1'
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
def join_room(sid, room):
    room_name = room['name']
    print(f'{sid} joined a room named {room_name}')
    i = [g.name for g in games].index(room_name)
    if games[i].password != '' and games[i].password != room['password'].upper():
        return
    sio.leave_room(sid, 'lobby')
    sio.enter_room(sid, room_name)
    while len([p for p in games[i].players if p.name == sio.get_session(sid).name]):
        sio.get_session(sid).name += '_1'
    games[i].add_player(sio.get_session(sid))
    advertise_lobbies()

@sio.event
def chat_message(sid, msg):
    ses = sio.get_session(sid)
    sio.emit('chat_message', room=ses.game.name, data=f'[{ses.name}]: {msg}')

@sio.event
def start_game(sid):
    ses = sio.get_session(sid)
    ses.game.start_game()

@sio.event
def set_character(sid, name):
    ses = sio.get_session(sid)
    ses.set_character(name)

@sio.event
def refresh(sid):
    ses = sio.get_session(sid)
    ses.notify_self()

@sio.event
def draw(sid, pile):
    ses = sio.get_session(sid)
    ses.draw(pile)

@sio.event
def pick(sid):
    ses = sio.get_session(sid)
    ses.pick()

@sio.event
def end_turn(sid):
    ses = sio.get_session(sid)
    ses.end_turn()

@sio.event
def play_card(sid, data):
    ses = sio.get_session(sid)
    ses.play_card(data['index'], data['against'])

@sio.event
def respond(sid, data):
    ses = sio.get_session(sid)
    ses.respond(data)

@sio.event
def choose(sid, card_index):
    ses = sio.get_session(sid)
    ses.choose(card_index)

@sio.event
def scrap(sid, card_index):
    ses = sio.get_session(sid)
    ses.scrap(card_index)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

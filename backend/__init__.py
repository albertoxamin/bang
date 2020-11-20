import eventlet
import socketio

from game import Game
from players import Player

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

games = []

def advertise_lobbies():
    sio.emit('lobbies', room='lobby', data=[{'name': g.name, 'players': len(g.players)} for g in games if not g.started])

@sio.event
def connect(sid, environ):
    print('connect ', sid)
    sio.enter_room(sid, 'lobby')

@sio.event
def set_username(sid, username):
    sio.save_session(sid, Player(username, sid))
    print(f'{sid} is now {username}')
    advertise_lobbies()

@sio.event
def my_message(sid, data):
    print('message ', data)

@sio.event
def disconnect(sid):
    if sio.get_session(sid).disconnect():
        games.pop(games.index(sio.get_session(sid).game))
    print('disconnect ', sid)
    advertise_lobbies()

@sio.event
def create_room(sid, room_name):
    sio.leave_room(sid, 'lobby')
    sio.enter_room(sid, room_name)
    g = Game(room_name, sio)
    g.add_player(sio.get_session(sid))
    games.append(g)
    print(f'{sid} created a room named {room_name}')
    advertise_lobbies()

@sio.event
def join_room(sid, room_name):
    print(f'{sid} joined a room named {room_name}')
    sio.leave_room(sid, 'lobby')
    sio.enter_room(sid, room_name)
    i = [g.name for g in games].index(room_name)
    games[i].add_player(sio.get_session(sid))
    advertise_lobbies()

@sio.event
def chat_message(sid, msg):
    ses = sio.get_session(sid)
    sio.emit('chat_message', room=ses.game.name, data=f'[{ses.name}]: {msg}')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

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
    sio.emit('lobbies', room='lobby', data=[{'name': g.name, 'players': g.players} for g in games if not g.started])

@sio.event
def connect(sid, environ):
    print('connect ', sid)
    sio.enter_room(sid, 'lobby')

@sio.event
def set_username(sid, username):
    sio.save_session(sid, Player(username))
    print(f'{sid} is now {username}')
    advertise_lobbies()

@sio.event
def my_message(sid, data):
    print('message ', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def create_room(sid, room_name):
    sio.leave_room(sid, 'lobby')
    g = Game(room_name)
    g.add_player(sio.get_session(sid))
    games.append(g)
    sio.enter_room(sid, room_name)
    print(f'{sid} created a room named {room_name}')
    advertise_lobbies()

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)

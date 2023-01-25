
class DummySocket():
    def __init__(self, sio=None):
        self.true_sio = sio

    def emit(self, event, data=None, to=None, room=None, skip_sid=None, namespace=None, callback=None, **kwargs):
        # print(f'event: {event}, data: {data}, to: {to}, room: {room}')
        if self.true_sio and event == 'chat_message':
            self.true_sio.emit(event, data, to, room, skip_sid, namespace, callback, **kwargs)
        return True
    
    def sleep(self, seconds):
        return seconds
    is_fake = True
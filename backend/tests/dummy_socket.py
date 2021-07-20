
class DummySocket():
    def emit(self, event, data=None, to=None, room=None, skip_sid=None, namespace=None, callback=None, **kwargs):
        # print(f'event: {event}, data: {data}, to: {to}, room: {room}')
        return True
    is_fake = True

class DummySocket():
    def emit(self, event, data=None, to=None, room=None, skip_sid=None, namespace=None, callback=None, **kwargs):
        return True
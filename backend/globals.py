from enum import IntEnum


class G:
    sio = None

    def __init__(self):
        pass


class PendingAction(IntEnum):
    PICK = 0
    DRAW = 1
    PLAY = 2
    RESPOND = 3
    WAIT = 4
    CHOOSE = 5

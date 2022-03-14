

class Event:
    def __init__(self, name="", source=0, e_type=0,  *args):
        self._event = name
        self._source = source
        self._type = e_type
        self._args = args

    @property
    def source(self):
        return self._source

    @property
    def type(self):
        return self._type

    @property
    def event(self):
        return self._event

    @property
    def args(self):
        return self._args


class StopMove(Event):
    pass


class MoveUp(Event):
    pass


class MoveRight(Event):
    pass


class MoveDown(Event):
    pass


class MoveLeft(Event):
    pass


class Attack(Event):
    pass


class Collecting(Event):
    pass


class Resting(Event):
    pass


class UseItem(Event):
    pass


class InputEvent(Event):
    pass

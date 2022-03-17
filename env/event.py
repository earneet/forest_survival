class Event:
    def __init__(self, name="", source=0, e_type=0, *args):
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


class CollectEnd(Event):
    def __init__(self, src, dest):
        super(CollectEnd, self).__init__()
        self.src = src
        self.dest = dest


class Resting(Event):
    pass


class UseItem(Event):
    def __init__(self, idx):
        super(UseItem, self).__init__()
        self.idx = idx


class DropItem(Event):
    def __init__(self, idx):
        super(DropItem, self).__init__()
        self.idx = idx


class MakeItem(Event):
    def __init__(self, item):
        super(MakeItem, self).__init__()
        self.item = item


class UnEquip(Event):
    def __init__(self, idx):
        super(UnEquip, self).__init__()
        self.idx = idx


class InputEvent(Event):
    pass


class Exchange(Event):
    def __init__(self, idx, direction):
        super(Exchange, self).__init__()
        self.idx = idx
        self.dir = direction

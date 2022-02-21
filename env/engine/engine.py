from . import GameItem


class Engine:
    def __init__(self, event_reader=None):
        self.game_items = {}
        self.event_reader = event_reader

    def render(self):
        pass

    def reset(self):
        pass

    def spawn(self, game_item: GameItem, parent: GameItem = None):
        assert game_item is not None, "game item can't be None Value"
        if game_item.id in self.game_items:
            return

        self.game_items[game_item.id] = game_item
        if parent is not None:
            parent.add_child(game_item)

    def update(self):
        # put draw canvas code here
        pass

    def user_event(self, event):
        if self.event_reader:
            self.event_reader(event)

    @staticmethod
    def get_instance():
        return _engine


_engine = Engine()


def get_engine():
    return _engine


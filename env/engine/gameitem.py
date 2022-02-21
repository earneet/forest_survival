import abc
import itertools
from collections import OrderedDict

id_counter = itertools.count()
next(id_counter)


class GameItem(abc.ABC):
    def __init__(self, parent: 'GameItem' = None):
        self.gi_id = next(id_counter)
        self.parent = parent
        self.children: OrderedDict = OrderedDict()
        self.components = []

    def get_id(self) -> int:
        return self.gi_id

    def get_parent(self):
        return self.parent

    def add_component(self, component):
        pass

    def render(self):
        pass

    def add_child(self, game_item: 'GameItem'):
        assert game_item is not None, "game_item can't be none"
        assert game_item.parent is None, "can't add a branch item"
        if game_item.gi_id in self.children:
            return
        self.children[game_item.gi_id] = game_item

    def _add_child(self, game_item):
        assert game_item is not None, "game_item can't be none"
        self.children[game_item.gi_id] = game_item

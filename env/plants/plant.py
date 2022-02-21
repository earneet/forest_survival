import abc

from env.engine.gameitem import GameItem


class Plant(GameItem, abc.ABC):
    def __init__(self):
        super().__init__()

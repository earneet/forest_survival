import abc
from enum import Enum
from typing import Dict

from env.engine.gameitem import GameItem

class AnimalState(Enum):
    IDLE = 0
    MOVING = 1
    BATTLING = 2


class Animal(GameItem, abc.ABC):
    def __init__(self, cfg, logic=None):
        super().__init__()
        self.hp = 1
        self.cfg = cfg
        self.move_speed = 1
        self.resource = {}
        self.ai_instance = None
        self._species = 'sheep'
        self.state = AnimalState.IDLE
        self._logic = logic

    def update(self):
        if self._logic:
            self._logic.update()

        if self.ai_instance:
            self.ai_instance.update()

    def species(self) -> str:
        raise NotImplementedError

    def drop_items(self) -> Dict[int, int]:
        raise NotImplementedError

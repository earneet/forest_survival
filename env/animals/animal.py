import abc
from enum import Enum

import numpy as np

from env.engine.gameitem import GameItem

class AnimalState(Enum):
    IDLE = 0
    MOVING = 1
    BATTLING = 2


class Animal(GameItem, abc.ABC):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.hp = int(cfg.attribute.hp)
        self.position = np.array([0, 0])
        self.move_speed = int(cfg.attribute.speed)
        self.ai_instance = None
        self._species = cfg.species
        self._logic = None
        self.state = AnimalState.IDLE
        self.killer = None
        self.attack_frame = 0                       # attack settlement frame
        self.damage_table = {}
        self.events = []

    def get_name(self):
        return self._species + "_" + self.id

    def update(self):
        if self._logic:
            self._logic.update()

        if self.ai_instance:
            self.ai_instance.update()

    def drop(self):
        return self._logic.drop()

    @property
    def species(self) -> str:
        return self._species

    def damage_by(self, attacker, damage):
        real_damage = self._logic.damage_by(attacker, damage)
        return real_damage

import random
from enum import Enum
from typing import Dict

import numpy as np

class AnimalState(Enum):
    IDLE = 0
    MOVING = 1
    BATTLING = 2


class Animal:

    is_player = False
    is_animal = True
    is_plant = False

    def __init__(self, cfg, env):
        assert env is not None
        super().__init__()
        self.cfg = cfg
        self.env = env
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
        return self._species

    def update(self):
        if self._logic:
            self._logic.update()

        if self.ai_instance:
            self.ai_instance.update()

    def is_dead(self):
        return self.hp <= 0

    @staticmethod
    def can_damage_by(attacker):
        from env.player import Player
        return True if isinstance(attacker, Player) else False

    @property
    def species(self) -> str:
        return self._species

    def damage_by(self, attacker, damage):
        real_damage = self._logic.damage_by(attacker, damage)
        return real_damage

    def drop(self) -> Dict[str, int]:
        drop_items = {}
        drop_cfg = self.cfg.drop or {}
        for item, drop_cfg in drop_cfg.items():
            old_cnt = drop_items[item] if item in drop_items else 0
            cnt = 0
            if isinstance(drop_cfg, int):
                cnt = drop_cfg
            elif isinstance(drop_cfg, float):
                cnt = 1 if random.random() < drop_cfg else 0
            elif isinstance(drop_cfg, list) or isinstance(drop_cfg, tuple):
                if len(drop_cfg) >= 2:
                    cnt = random.randint(drop_cfg[0], drop_cfg[1])
                else:
                    cnt = 0
            drop_items[item] = max(cnt, 0) + old_cnt

        return drop_items

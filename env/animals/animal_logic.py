import random
from typing import Dict


class AnimalMoveLogic:
    def __init__(self, animal, logic):
        self.animal = animal
        self.owner_logic = logic

class AnimalLogic:
    def __init__(self, animal):
        self.animal = animal

    def update(self):
        pass

    def drop(self) -> Dict[str, int]:
        drop_items = {}
        drop_cfg = self.animal.cfg.drop or {}
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

    def damage_by(self, attacker, damage):
        animal = self.animal
        if animal.hp <= 0:
            return 0
        animal.hp -= damage
        if animal.hp <= 0:
            animal.killer = attacker
        return damage

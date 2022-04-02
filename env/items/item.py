from typing import Optional, Dict

from env.items import clothes_cfg, equip_cfg


class Item:
    def __init__(self, item_id):
        self.id = item_id


class Equip:
    def __init__(self, cfg):
        self.cfg = cfg
        self.wear = cfg.wear

    def name(self):
        return self.cfg.name

    def get_attack(self) -> int:
        return self.cfg.attack


class Cloth:
    def __init__(self, cfg):
        self.cfg = cfg
        self.wear = cfg.wear

    def name(self):
        return self.cfg.name

    def get_temperature_delta(self) -> int:
        return self.cfg.effect.temperature


def make_cloth(item_id) -> Cloth:
    from env.items import clothes_cfg
    cloth_cfg = clothes_cfg[item_id]
    if cloth_cfg:
        return Cloth(cloth_cfg)


def make_equip(item_id) -> Equip:
    cfg = equip_cfg[item_id]
    if equip_cfg:
        return Equip(cfg)


def make_common_item(item_id) -> Item:
    return Item(item_id)


def make_item(item_id: str):
    if item_id is None:
        return None

    if item_id.endswith("_clothes"):
        return make_cloth(item_id)
    elif item_id.endswith("_equip"):
        return make_equip(item_id)
    else:
        return make_common_item(item_id)


def get_recipe_materials(item: str) -> Optional[Dict[str, int]]:
    item_cfgs = clothes_cfg if item.endswith("_clothes") else equip_cfg
    for name, cfg in item_cfgs.items():
        if name == item:
            return cfg.recipe.materials
    return None

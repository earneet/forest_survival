import pkgutil
import json
from munch import DefaultMunch

raw_data = pkgutil.get_data(__package__, "../../gamecfg/clothes.json")
clothes_cfg = raw_data.decode()
clothes_cfg = json.loads(clothes_cfg)
clothes_cfg = DefaultMunch.fromDict(clothes_cfg)

raw_data = pkgutil.get_data(__package__, "../../gamecfg/equip.json")
equip_cfg = raw_data.decode()
equip_cfg = json.loads(equip_cfg)
equip_cfg = DefaultMunch.fromDict(equip_cfg)

raw_data = pkgutil.get_data(__package__, "../../gamecfg/prop.json")
prop_cfg = raw_data.decode()
prop_cfg = json.loads(prop_cfg)
prop_cfg = DefaultMunch.fromDict(prop_cfg)

foods = set()
materials = set()
hp_recovers = set()
hunger_recovers = set()

for name, cfg in prop_cfg.items():
    if "food" in cfg.categories:
        foods.add(name)
    if "material" in cfg.categories:
        materials.add(name)
    if cfg.effect.hp and cfg.effect.hp > 0:
        hp_recovers.add(name)
    if cfg.effect.hunger and cfg.effect.hunger > 0:
        hunger_recovers.add(name)


def is_food(item) -> bool:
    if not isinstance(item, str):
        return False
    return item in foods

def can_recover_hp(item) -> bool:
    return item in hp_recovers

def can_recover_hunger(item) -> bool:
    return item in hunger_recovers

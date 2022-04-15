from typing import Iterable

from .animal_config import animal_cfg, drop_equipment_animals
from .event import *
from .plant_config import drop_equipment_plants, plant_cfg
from .terrain import Terrain, string2terrains
from .player_state import PlayerState, SlotType, CLOTHES_SLOT
from .player_config import player_cfg, init_cfg
from .move_type import MoveType
from .direction import DirectionEnum, get_vec_by_direction
from ..items import prop_cfg

drop_equipment_beings = (*drop_equipment_animals, *drop_equipment_plants)

drop_food_animals = []
drop_food_plants = []


for name, cfg in animal_cfg.items():
    for n, _ in cfg.drop.items():
        if not n.endswith('_equip') and not n.endswith('_clothes'):
            if "hunger" in prop_cfg[n].effect:
                drop_food_animals.append(name)

for name, cfg in plant_cfg.items():
    for n, _ in cfg.drop.items():
        if not n.endswith('_equip') and not n.endswith('_clothes'):
            if "hunger" in prop_cfg[n].effect:
                drop_food_plants.append(name)

drop_food_beings = (*drop_food_animals, *drop_food_plants)

def get_drop_equipment_beings() -> Iterable[str]:
    return drop_equipment_beings

def get_drop_food_beings() -> Iterable[str]:
    return drop_food_beings

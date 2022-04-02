from typing import Iterable

from .animal_config import drop_equipment_animals
from .event import *
from .plant_config import drop_equipment_plants
from .terrain import Terrain, string2terrains
from .player_state import PlayerState, SlotType, CLOTHES_SLOT
from .player_config import player_cfg, init_cfg
from .move_type import MoveType
from .direction import DirectionEnum, get_vec_by_direction

drop_equipment_beings = (*drop_equipment_animals, *drop_equipment_plants)

def get_drop_equipment_beings() -> Iterable[str]:
    return drop_equipment_beings



from .plant import Plant
from .plant_config import plant_cfg

def new_plant(specie, env):
    cfg = plant_cfg[specie]
    return Plant(cfg, env)

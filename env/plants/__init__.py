

from .plant import Plant
from env.common.plant_config import plant_cfg

def new_plant(specie, env):
    cfg = plant_cfg[specie]
    return Plant(cfg, env)

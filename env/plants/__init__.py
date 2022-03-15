

import pkgutil
import json
from munch import DefaultMunch
from .plant import Plant

raw_data = pkgutil.get_data(__package__, "../../gamecfg/plant.json")
plant_cfg = raw_data.decode()
plant_cfg = json.loads(plant_cfg)
plant_cfg = DefaultMunch.fromDict(plant_cfg)


def new_plant(specie, env):
    cfg = plant_cfg[specie]
    return Plant(cfg, env)

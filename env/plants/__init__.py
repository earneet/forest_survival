

import pkgutil
import json
from .plant import Plant

raw_data = pkgutil.get_data(__package__, "../../gamecfg/plant.json")
plant_cfg = raw_data.decode()
plant_cfg = json.loads(plant_cfg)


def new_plant(specie):
    cfg = plant_cfg[specie]
    return Plant(cfg)

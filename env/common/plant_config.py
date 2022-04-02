import json
import os
from typing import List

from munch import DefaultMunch

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, "../../gamecfg/plant.json")) as f:
    plant_cfg = f.read()
plant_cfg = json.loads(plant_cfg)
plant_cfg = DefaultMunch.fromDict(plant_cfg)


drop_equipment_plants = []

for name, cfg in plant_cfg.items():
    for n, _ in cfg.drop.items():
        if n.endswith('_equip'):
            drop_equipment_plants.append(name)
            break

drop_equipment_plants = tuple(drop_equipment_plants)

def get_drop_equipment_plants() -> List[str]:
    return drop_equipment_plants

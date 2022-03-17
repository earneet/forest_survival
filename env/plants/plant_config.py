import json
import os
# import pkgutil

from munch import DefaultMunch

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, "../../gamecfg/plant.json")) as f:
    plant_cfg = f.read()
# raw_data = pkgutil.get_data(__package__, "../../gamecfg/plant.json")
# plant_cfg = raw_data.decode()
plant_cfg = json.loads(plant_cfg)
plant_cfg = DefaultMunch.fromDict(plant_cfg)

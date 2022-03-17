# import pkgutil
import json
import os

from munch import DefaultMunch

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, "../../gamecfg/animal.json")) as f:
    animal_cfg = f.read()

# raw_data = pkgutil.get_data(__package__, "../../gamecfg/animal.json")
# animal_cfg = raw_data.decode()
animal_cfg = json.loads(animal_cfg)
animal_cfg = DefaultMunch.fromDict(animal_cfg)

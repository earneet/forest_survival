
import pkgutil
import json

raw_data = pkgutil.get_data(__package__, "../../gamecfg/animal.json")
animal_cfg = raw_data.decode()
animal_cfg = json.loads(animal_cfg)

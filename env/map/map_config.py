import json
import os

from munch import DefaultMunch

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, "../../gamecfg/map.json")) as f:
    map_cfg = f.read()

map_cfg = json.loads(map_cfg)
map_cfg = DefaultMunch.fromDict(map_cfg)

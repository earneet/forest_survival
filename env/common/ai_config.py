import json
import os

from munch import DefaultMunch

disposition_configs = {}

file_path = os.path.dirname(__file__)
ai_config_dir = os.path.join(file_path, "../../gamecfg/ai/")
g = os.walk(ai_config_dir)
for path, dir_list, file_list in g:
    for file_name in file_list:
        with open(os.path.join(path, file_name)) as f:
            cfg = json.loads(f.read())
            disposition_configs[file_name[:-5]] = DefaultMunch.fromDict(cfg)

def get_ai_config(disposition: str):
    if disposition in disposition_configs:
        return disposition_configs[disposition]

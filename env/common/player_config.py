import json
import pkgutil

from munch import DefaultMunch

raw_data = pkgutil.get_data(__package__, "../../gamecfg/player.json")
player_cfg = raw_data.decode()
player_cfg = json.loads(player_cfg)
player_cfg = DefaultMunch.fromDict(player_cfg)

raw_data = pkgutil.get_data(__package__, "../../gamecfg/init.json")
init_cfg = raw_data.decode()
init_cfg = json.loads(init_cfg)
init_cfg = DefaultMunch.fromDict(init_cfg)


import pkgutil
import json

raw_data = pkgutil.get_data(__package__, "../../gamecfg/clothes.json")
clothes_cfg = raw_data.decode()
clothes_cfg = json.loads(clothes_cfg)

raw_data = pkgutil.get_data(__package__, "../../gamecfg/equip.json")
equip_cfg = raw_data.decode()
equip_cfg = json.loads(equip_cfg)


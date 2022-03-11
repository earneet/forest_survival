
import pkgutil
import json
from munch import DefaultMunch
from .item import make_item
from .item import make_cloth
from .item import make_equip

raw_data = pkgutil.get_data(__package__, "../../gamecfg/clothes.json")
clothes_cfg = raw_data.decode()
clothes_cfg = json.loads(clothes_cfg)
clothes_cfg = DefaultMunch.fromDict(clothes_cfg)

raw_data = pkgutil.get_data(__package__, "../../gamecfg/equip.json")
equip_cfg = raw_data.decode()
equip_cfg = json.loads(equip_cfg)
equip_cfg = DefaultMunch.fromDict(equip_cfg)

raw_data = pkgutil.get_data(__package__, "../../gamecfg/prop.json")
prop_cfg = raw_data.decode()
prop_cfg = json.loads(prop_cfg)
prop_cfg = DefaultMunch.fromDict(prop_cfg)


__all__ = ['make_equip', 'make_item', 'make_cloth', 'equip_cfg', 'clothes_cfg', 'prop_cfg']

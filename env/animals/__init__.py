
import pkgutil
import json
from animal import Animal
from sheep import Sheep
from cattle import Cattle
from chick import Chick

specie_classes = {
    'sheep': Sheep,
    'cattle': Cattle,
    'chick': Chick
}

raw_data = pkgutil.get_data(__package__, "../../gamecfg/animal.json")
animal_cfg = raw_data.decode()
animal_cfg = json.loads(animal_cfg)

def new_animal(specie, cfg):
    clazz = specie_classes[specie]
    return clazz(cfg)

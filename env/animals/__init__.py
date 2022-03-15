
import pkgutil
import json
from munch import DefaultMunch
from .animal import Animal
from .animal_logic import AnimalLogic

raw_data = pkgutil.get_data(__package__, "../../gamecfg/animal.json")
animal_cfg = raw_data.decode()
animal_cfg = json.loads(animal_cfg)
animal_cfg = DefaultMunch.fromDict(animal_cfg)


def new_animal(specie, env):
    assert specie in animal_cfg
    cfg = animal_cfg[specie]
    ani = Animal(cfg, env)
    ani._logic = AnimalLogic(ani)
    return ani


import pkgutil
import json
from animal import Animal
from animal_logic import AnimalLogic

raw_data = pkgutil.get_data(__package__, "../../gamecfg/animal.json")
animal_cfg = raw_data.decode()
animal_cfg = json.loads(animal_cfg)

def new_animal(specie, cfg):
    ani = Animal(specie, cfg)
    ani._logic = AnimalLogic(ani)
    return ani


from .animal import Animal
from .animal_config import animal_cfg
from .animal_logic import AnimalLogic

def new_animal(specie, env):
    assert specie in animal_cfg
    cfg = animal_cfg[specie]
    ani = Animal(cfg, env)
    ani._logic = AnimalLogic(ani)
    return ani

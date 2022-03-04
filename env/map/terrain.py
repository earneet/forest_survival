from enum import Enum


class Terrain(Enum):
    SELF_HOUSE = 1  # npc house
    HOUSE = 2   # other npc's house
    FOREST = 3
    RIVER = 4
    LAWN = 5


def string2terrains(terrains):
    if isinstance(terrains, str):
        terrains = terrains.split(',')
    assert isinstance(terrains, list)
    return [Terrain[t.strip().upper()] for t in terrains]


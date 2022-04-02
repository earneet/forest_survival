import json
import os
from enum import IntEnum

from munch import DefaultMunch

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, "../../gamecfg/terrain.json")) as f:
    terrain_cfg = f.read()

terrain_cfg = json.loads(terrain_cfg)
terrain_cfg = DefaultMunch.fromDict(terrain_cfg)


class Terrain(IntEnum):
    INVALID = 0
    SELF_HOUSE = 1  # npc house
    HOUSE = 2  # other npc's house
    FOREST = 3
    RIVER = 4
    LAWN = 5


TerrainTemperature = {
    Terrain.SELF_HOUSE: 0,
    Terrain.HOUSE: 0,
    Terrain.FOREST: 0,
    Terrain.LAWN: 0,
    Terrain.RIVER: -5
}


def string2terrains(terrains):
    if isinstance(terrains, str):
        terrains = terrains.split(',')
    assert isinstance(terrains, list)
    return [Terrain[t.strip().upper()] for t in terrains]


TerrainTravelCost = {}

for name, cfg in terrain_cfg.items():
    TerrainTravelCost[string2terrains(name)[0]] = cfg.player_cost


def get_temperature_delta(terrain):
    return TerrainTemperature[terrain]


def get_playercost(terrain, game_obj, interest="time"):
    assert isinstance(terrain, Terrain), "terrain must be a Terrain instance"
    return TerrainTravelCost[terrain]

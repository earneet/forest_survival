import logging

from env.common import Terrain
from .mapcell_logic import MapLogicHouse, MapLogicCommon, MapLogicForest, MapLogicRiver
from ..animals import Animal
from ..common.terrain import get_temperature_delta, get_playercost
from ..plants import Plant
from ..player import Player

Terrain2Logic = {
    Terrain.SELF_HOUSE: MapLogicHouse,
    Terrain.HOUSE: MapLogicHouse,
    Terrain.FOREST: MapLogicForest,
    Terrain.LAWN: MapLogicCommon,
    Terrain.RIVER: MapLogicRiver
}


class MapCell:
    def __init__(self, x, y, terrain: Terrain = Terrain.LAWN):
        self.x = x
        self.y = y
        self.type = terrain
        self.plants = []
        self.animals = []
        self.players = []
        self.owner = None       # when the type is HOUSE, it can have an owner, else None
        self._logic = Terrain2Logic[terrain](self)

    def spawn_plant(self, plant):
        self.plants.append(plant)

    def spawn_animal(self, animal):
        self.animals.append(animal)

    def can_move_in(self, game_obj):
        return self._logic.can_move_in(game_obj)

    def traversing_cost(self, game_obj=None, interest="time") -> float:
        return get_playercost(self.type, game_obj, interest)

    def move_out(self, game_obj):
        container = None
        if isinstance(game_obj, Player):
            container = self.players
        elif isinstance(game_obj, Animal):
            container = self.animals
        if game_obj not in container:
            logging.warning("Bug Happend, to solved this")
        else:
            container.remove(game_obj)
        return self._logic.on_move_out(game_obj)

    def move_in(self, game_obj):
        if isinstance(game_obj, Player):
            self.players.append(game_obj)
        elif isinstance(game_obj, Animal):
            self.animals.append(game_obj)
        self._logic.on_move_in(game_obj)

    def remove_dead(self, game_obj):
        if isinstance(game_obj, Player):
            self.players.remove(game_obj)
        elif isinstance(game_obj, Animal):
            self.animals.remove(game_obj)
        elif isinstance(game_obj, Plant):
            self.plants.remove(game_obj)

    def get_temperature_delta(self):
        return get_temperature_delta(self.type)

    def is_empty(self):
        return not (self.plants or self.animals or self.players)

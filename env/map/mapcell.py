
from env.common import Terrain
from .mapcell_logic import MapLogicHouse, MapLogicCommon, MapLogicForest, MapLogicRiver

Terrain2Logic = {
    Terrain.SELF_HOUSE: MapLogicHouse,
    Terrain.HOUSE: MapLogicHouse,
    Terrain.FOREST: MapLogicForest,
    Terrain.LAWN: MapLogicCommon,
    Terrain.RIVER: MapLogicRiver
}

TerrainTemperature = {
    Terrain.SELF_HOUSE: 0,
    Terrain.HOUSE: 0,
    Terrain.FOREST: 0,
    Terrain.LAWN: 0,
    Terrain.RIVER: -5
}


class MapCell:
    def __init__(self, x, y, terrain: Terrain = Terrain.LAWN):
        self.x = x
        self.y = y
        self.type = terrain
        self.plants = []
        self.animals = []
        self.players = []
        self._logic = Terrain2Logic[terrain](self)

    def spawn_plant(self, plant):
        self.plants.append(plant)

    def spawn_animal(self, animal):
        self.animals.append(animal)

    def player_can_move_in(self, player):
        return self._logic.can_move_in(player)

    def player_move_out(self, player):
        return self._logic.on_player_move_out(player)

    def get_temperature_delta(self):
        return TerrainTemperature[self.type]

    def player_move_in(self, player):
        if player in self.players:
            return
        self.players.append(player)
        self._logic.on_player_move_in(player)

    def is_empty(self):
        return not (self.plants or self.animals or self.players)

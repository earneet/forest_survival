import abc

from player import PlayerState, Player
from player.player import MoveType
from . import Terrain


class MapLogicBase(abc.ABC):
    def __init__(self, cell):
        self.cell = cell

    def can_move_in(self, player):
        assert player is not None
        return True

    def on_player_move_in(self, player):
        if player.sub_state == MoveType.SWIMMING and len(player.sub_state_stack) > 0:
            player.sub_state = player.sub_state_stack.pop()

    def on_player_move_out(self, player):
        pass

    def on_player_start_move(self, player):
        pass


class MapLogicCommon(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)


class MapLogicRiver(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def can_move_in(self, player):
        if isinstance(player, Player):
            return True
        return False

    def on_player_move_in(self, player):
        if player.state == PlayerState.MOVING and player.sub_state != MoveType.SWIMMING:
            player.sub_state_stack.append(player.sub_state)
            player.sub_state = MoveType.SWIMMING

    def on_player_start_move(self, player):
        player.sub_state = MoveType.SWIMMING


class MapLogicForest(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def on_player_move_in(self, player):
        if player.state == PlayerState.MOVING and player.sub_state == MoveType.RUNNING:
            player.sub_state_stack.append(player.sub_state)
            player.sub_state = MoveType.WALKING

    def on_player_move_out(self, player):
        player.sub_state = player.sub_state_stack.pop()

    def on_player_start_move(self, player):
        player.sub_state = MoveType.WALKING


class MapLogicHouse(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def on_player_start_move(self, player):
        pass


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
    Terrain.RIVER:0
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

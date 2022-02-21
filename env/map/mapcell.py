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
        pass

    def on_player_move_out(self, player):
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
        if player.state == PlayerState.MOVING:
            player.sub_state = MoveType.SWIMMING

    def on_player_move_out(self, player):
        pass


class MapLogicHouse(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)


Terrain2Logic = {
    Terrain.SELF_HOUSE: MapLogicHouse,
    Terrain.HOUSE: MapLogicHouse,
    Terrain.FOREST: MapLogicCommon,
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
        self._logic = Terrain2Logic[terrain](self)

    def player_can_move_in(self, player):
        return self._logic.can_move_in(player)

    def player_move_out(self, player):
        return self._logic.on_player_move_out(player)

    def player_move_in(self, player):
        if player in self.players:
            return
        self.players.append(player)
        self._logic.on_player_move_in(player)

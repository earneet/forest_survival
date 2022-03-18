import abc

from env.common import MoveType, PlayerState
from env.player import Player


class MapLogicBase(abc.ABC):
    def __init__(self, cell):
        self.cell = cell

    def can_move_in(self, game_obj):
        assert game_obj is not None
        return True

    def on_move_in(self, game_obj):
        if not isinstance(game_obj, Player):
            return
        if game_obj.sub_state == MoveType.SWIMMING and len(game_obj.sub_state_stack) > 0:
            game_obj.sub_state = game_obj.sub_state_stack.pop()

    def on_move_out(self, game_obj):
        pass

    def on_start_move(self, game_obj):
        pass


class MapLogicCommon(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)


class MapLogicRiver(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def can_move_in(self, game_obj):
        if isinstance(game_obj, Player):
            return True
        return False

    def on_move_in(self, game_obj):
        if not isinstance(game_obj, Player):
            return
        if game_obj.state == PlayerState.MOVING and game_obj.sub_state != MoveType.SWIMMING:
            game_obj.sub_state_stack.append(game_obj.sub_state)
            game_obj.sub_state = MoveType.SWIMMING

    def on_start_move(self, game_obj):
        if not isinstance(game_obj, Player):
            return
        game_obj.sub_state = MoveType.SWIMMING


class MapLogicForest(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def on_move_in(self, game_obj):
        if not isinstance(game_obj, Player):
            return
        if game_obj.state == PlayerState.MOVING:
            game_obj.sub_state_stack.append(game_obj.sub_state)
            game_obj.sub_state = MoveType.WALKING

    def on_move_out(self, game_obj):
        if not isinstance(game_obj, Player):
            return
        if len(game_obj.sub_state_stack):
            game_obj.sub_state = game_obj.sub_state_stack.pop()

    def on_start_move(self, game_obj):
        if not isinstance(game_obj, Player):
            return
        game_obj.sub_state = MoveType.WALKING


class MapLogicHouse(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def on_start_move(self, game_obj):
        pass

import abc

from env.player import MoveType, Player, PlayerState


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
        if player.state == PlayerState.MOVING:
            player.sub_state_stack.append(player.sub_state)
            player.sub_state = MoveType.WALKING

    def on_player_move_out(self, player):
        if len(player.sub_state_stack):
            player.sub_state = player.sub_state_stack.pop()

    def on_player_start_move(self, player):
        player.sub_state = MoveType.WALKING


class MapLogicHouse(MapLogicBase):
    def __init__(self, cell):
        super().__init__(cell)

    def on_player_start_move(self, player):
        pass



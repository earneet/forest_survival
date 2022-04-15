import numpy as np

from env.AI.path import find_path
from env.common import *
from env.player.logic.concretelogic.concrete_logic import PlayerConcreteLogic
from env.common.player_config import player_cfg


class PlayerMoveLogic(PlayerConcreteLogic):
    event2direction = {
        MoveUp: DirectionEnum.UP,
        MoveRight: DirectionEnum.RIGHT,
        MoveDown: DirectionEnum.DOWN,
        MoveLeft: DirectionEnum.LEFT
    }

    def __init__(self, player, logic):
        super(PlayerMoveLogic, self).__init__(player, logic)
        self.target_pos = None
        self.path = None
        self.map = player.env.map

    def on_enter_state(self, type_or_pos, orientation=DirectionEnum.INVALID):
        if orientation != DirectionEnum.INVALID:
            self.enter_with_op(type_or_pos, orientation)
        else:
            self.enter_with_tar(type_or_pos)

    def enter_with_op(self, speed_type, orientation):
        self.player.state = PlayerState.MOVING
        self.player.sub_state = speed_type
        self.player.direction = orientation

    def enter_with_tar(self, pos):
        if self.target_pos and np.linalg.norm(pos-self.target_pos) < 2:
            self.target_pos = pos
            return

        world_map = self.player.env.map
        cur_cell = world_map.get_cell_by_pos(self.player.position)
        target_cell = world_map.get_cell_by_pos(pos)
        path_cells = find_path(self.player, cur_cell, target_cell, world_map)
        if not path_cells:
            self.path = [cur_cell]
        else:
            path_chain = path_cells[1:] if len(path_cells) > 1 else path_cells
            self.path = path_chain

        self.target_pos = pos
        self.player.state = PlayerState.MOVING
        self.player.sub_state = MoveType.RUNNING
        self.player.direction = self._compute_towards(self.player.position, self.map.get_cell_center(self.path[0]))

    def on_leave_state(self, *_):
        self.player.state = PlayerState.IDLE
        self.player.sub_state = None
        self.path = None
        self.target_pos = None
        self.parent_logic.cur_logic = None

    def update(self):
        if self.path:
            self.update_path()
        else:
            self.update_move()

    def update_path(self):
        position = self.player.position
        if not self.path:   # at the end cell
            tar_position = position + self.get_move_speed() * get_vec_by_direction(self.player.direction)
            if np.linalg.norm(self.target_pos - position) < 5:
                self.player.position = self.target_pos
                self.parent_logic.switch_state(self.parent_logic.idle_logic)
            else:
                new_orientation = self._compute_towards(tar_position, self.target_pos)
                self.player.direction = new_orientation
                self.player.position = tar_position

        cur_cell = self.path[0]
        orientation = self.player.direction
        tar_position = position + self.get_move_speed() * get_vec_by_direction(orientation)
        if not self._is_beyond_position(tar_position, self.map.get_cell_center(cur_cell), orientation):
            self.player.position = tar_position
            return

        self.path.pop(0)    # remove cur_cell
        next_cell = self.path[0] if self.path else None
        if next_cell:
            # diff = self._get_overflow_distance(tar_position, self.map.get_cell_center(cur_cell), orientation)
            # todo offset the overflow distance
            corner = tar_position
            way_point = self.map.get_cell_center(next_cell)
            new_orientation = self._compute_towards(corner, way_point)
            self.player.position = corner
            self.player.direction = new_orientation

    @staticmethod
    def _is_beyond_position(position, target, orientation) -> bool:
        diff = target - position
        if orientation == DirectionEnum.UP:
            return diff[1] > 0
        elif orientation == DirectionEnum.RIGHT:
            return diff[0] < 0
        elif orientation == DirectionEnum.DOWN:
            return diff[1] < 0
        elif orientation == DirectionEnum.LEFT:
            return diff[0] > 0
        return False

    @staticmethod
    def _get_overflow_distance(position, target, orientation) -> float:
        if orientation == DirectionEnum.UP:
            return target[1] - position[1]
        elif orientation == DirectionEnum.RIGHT:
            return position[0] - target[0]
        elif orientation == DirectionEnum.DOWN:
            return position[1] - target[1]
        elif orientation == DirectionEnum.LEFT:
            return target[0] - position[0]
        return 0

    @staticmethod
    def _compute_towards(src_pos, to_pos) -> DirectionEnum:
        x_diff = to_pos[0] - src_pos[0]
        y_diff = to_pos[1] - src_pos[1]
        if abs(x_diff) > abs(y_diff):
            return DirectionEnum.LEFT if x_diff < 0 else DirectionEnum.RIGHT
        else:
            return DirectionEnum.DOWN if y_diff > 0 else DirectionEnum.UP

    def update_move(self):
        player = self.player
        env = player.env
        speed = self.get_move_speed()
        cur_pos = player.position
        tar_pos = speed * get_vec_by_direction(player.direction) + cur_pos
        cur_cell = env.map.get_cell_by_pos(cur_pos)
        tar_cell = env.map.get_cell_by_pos(tar_pos)
        if not (tar_cell and tar_cell.can_move_in(player)):
            self._move_to_edge(cur_cell)
            self.parent_logic.switch_state(self.parent_logic.idle_logic)
            return
        player.position = tar_pos
        cur_cell.move_out(player)
        tar_cell.move_in(player)

    def get_move_speed(self):
        player = self.player
        env = player.env
        env.get_global_temperature()

        # move type speed
        if player.sub_state == MoveType.WALKING:
            speed = player_cfg.speed_walk * env.STEP_BREAK
        elif player.sub_state == MoveType.RUNNING:
            speed = player_cfg.speed_run * env.STEP_BREAK
        elif player.sub_state == MoveType.SWIMMING:
            speed = player_cfg.speed_swim * env.STEP_BREAK
        else:
            return 0

        # hunger effect
        if self.player.hunger < 5:
            speed = 0
        elif 5 <= self.player.hunger < 20:
            speed *= 0.5
        elif 20 <= self.player.hunger < 60:
            pass
        elif 60 <= self.player.hunger < 90:
            speed *= 1.2
        elif 90 <= self.player.hunger <= 100:
            speed *= 1.5
        return speed

    def process_event_stop(self, _):
        if self.player.state != PlayerState.MOVING:
            return
        self.parent_logic.switch_state(self.parent_logic.idle_logic)

    def process_event_move(self, move_event):
        if self.player.state != PlayerState.MOVING:
            cell = self.player.env.map.get_cell_by_pos(self.player.position)
            orientation = self.event2direction[move_event.__class__]
            self.parent_logic.switch_state(self, MoveType.RUNNING, orientation)
            if hasattr(cell, "on_player_start_move"):
                cell.on_start_move()

    def _move_to_edge(self, cell):
        player = self.player
        left, right, bottom, top = player.env.map.get_cell_edge(cell)
        orientation = player.direction
        pos = player.position
        if orientation == DirectionEnum.UP:
            pos[1] = top
        elif orientation == DirectionEnum.RIGHT:
            pos[0] = right
        elif orientation == DirectionEnum.DOWN:
            pos[1] = bottom
        elif orientation == DirectionEnum.LEFT:
            pos[0] = left
        player.position = pos

import random
from typing import Dict

from env.common.animal_state import AnimalState
from env.common.direction import DirectionEnum, get_vec_by_direction


class AnimalMoveLogic:
    def __init__(self, animal, logic):
        self.animal = animal
        self.owner_logic = logic
        self.target_point = None
        self.target_dir = None

    def on_enter_state(self, *_):
        self.animal.state = AnimalState.MOVING
        self.random_target_pos()

    def on_leave_state(self):
        self.animal.last_move_frame = self.animal.frames
        self.animal.next_move_frame = self.random_next_frame()

    def update(self):
        if self.target_dir != self.animal.direction:
            self.animal.direction = self.target_dir
        should_stop = False
        pos = self.animal.position
        direction = self.animal.direction
        target_pos = pos + self.get_move_speed() * self.animal.env.STEP_BREAK * get_vec_by_direction(direction)
        cur_cell = self.animal.env.map.get_cell_by_pos(pos)
        target_cell = self.animal.env.map.get_cell_by_pos(target_pos)
        if target_cell != cur_cell:
            if target_cell and target_cell.can_move_in(self.animal):
                cur_cell.move_out(self.animal)
                target_cell.move_in(self.animal)
            else:
                left, right, top, bottom = self.animal.env.map.get_cell_edge(cur_cell)
                if direction == DirectionEnum.UP:
                    target_pos[1] = top
                elif direction == DirectionEnum.RIGHT:
                    target_pos[0] = right
                elif direction == DirectionEnum.DOWN:
                    target_pos[1] = bottom
                elif direction == DirectionEnum.LEFT:
                    target_pos[0] = left
                should_stop = True

        if direction == DirectionEnum.UP and target_pos[1] >= self.target_point[1]:
            should_stop = True
            target_pos[1] = self.target_point[1]
        elif direction == DirectionEnum.RIGHT and target_pos[0] >= self.target_point[0]:
            should_stop = True
            target_pos[0] = self.target_point[0]
        elif direction == DirectionEnum.DOWN and target_pos[1] <= self.target_point[1]:
            should_stop = True
            target_pos[1] = self.target_point[1]
        elif direction == DirectionEnum.LEFT and target_pos[0] <= self.target_point[0]:
            should_stop = True
            target_pos[0] = self.target_point[0]
        self.animal.position = target_pos
        if should_stop:
            self.owner_logic.switch_state(self.owner_logic.idle_logic)

    def get_move_speed(self):
        return self.animal.speed

    def random_target_pos(self):
        distance = self._random_distance()
        direction = self._random_direction()
        target_point = self.animal.position + distance * get_vec_by_direction(direction)
        self.target_point = target_point
        self.target_dir = direction

    @staticmethod
    def _random_direction():
        return DirectionEnum(random.randint(DirectionEnum.UP, DirectionEnum.LEFT))

    def _random_distance(self):
        move_distance = self.animal.cfg.strategy.move.distance
        if isinstance(move_distance, list) and len(move_distance) >= 2:
            move_distance = random.random() * (move_distance[1] - move_distance[0]) + move_distance[0]
        return move_distance

    def random_next_frame(self):
        frame_range = self.animal.cfg.strategy.move.move_interval
        if isinstance(frame_range, list) and len(frame_range) >= 2:
            frame_range = random.random() * (frame_range[1] - frame_range[0]) + frame_range[0]
        return self.animal.frames + int(frame_range)


class AnimalIdleLogic:
    def __init__(self, animal, logic):
        self.animal = animal
        self.owner_logic = logic

    def on_enter_state(self, *_):
        self.animal.state = AnimalState.IDLE
        self.owner_logic.cur_logic = self

    def on_leave_state(self):
        pass

    def update(self):
        frames = self.animal.frames
        if frames >= self.animal.next_move_frame:
            self.owner_logic.switch_state(self.owner_logic.move_logic)


class AnimalLogic:
    def __init__(self, animal):
        self.animal = animal
        self.move_logic = AnimalMoveLogic(animal, self)
        self.idle_logic = AnimalIdleLogic(animal, self)
        self.cur_logic = self.idle_logic

    def update(self):
        if self.cur_logic:
            self.cur_logic.update()

    def switch_state(self, logic, *args):
        if self.cur_logic:
            self.cur_logic.on_leave_state()
        self.cur_logic = logic
        self.cur_logic.on_enter_state(*args)

    def on_leave_old_state(self):
        if self.cur_logic:
            self.cur_logic.on_leave_state()

    def drop(self) -> Dict[str, int]:
        drop_items = {}
        drop_cfg = self.animal.cfg.drop or {}
        for item, drop_cfg in drop_cfg.items():
            old_cnt = drop_items[item] if item in drop_items else 0
            cnt = 0
            if isinstance(drop_cfg, int):
                cnt = drop_cfg
            elif isinstance(drop_cfg, float):
                cnt = 1 if random.random() < drop_cfg else 0
            elif isinstance(drop_cfg, list) or isinstance(drop_cfg, tuple):
                if len(drop_cfg) >= 2:
                    cnt = random.randint(drop_cfg[0], drop_cfg[1])
                else:
                    cnt = 0
            drop_items[item] = max(cnt, 0) + old_cnt

        return drop_items

    def damage_by(self, attacker, damage):
        animal = self.animal
        if animal.hp <= 0:
            return 0
        animal.hp -= damage
        if animal.hp <= 0:
            animal.killer = attacker
        return damage

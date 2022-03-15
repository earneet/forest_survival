import enum
from enum import Enum, IntEnum
from typing import Dict, List, Tuple

from env.engine.gameitem import GameItem
import itertools
import numpy as np

from event import Event

player_id = itertools.count()
next(player_id)


class PlayerState(Enum):
    IDLE = 0        # 什么都没干
    MOVING = 1      # 在移动
    BATTLING = 2    # 在打架
    COLLECTING = 3  # 在收集
    RESTING = 4     # 在休整
    MAKING = 5      # 在制造


@enum.unique
class MoveType(IntEnum):
    WALKING = 0
    RUNNING = 1
    SWIMMING = 2


class SlotType(IntEnum):
    EQUIP = 0
    CLOTH = 1


@enum.unique
class DirectionEnum(IntEnum):
    INVALID = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


Direction2Vec = {
    DirectionEnum.UP: np.array([0, -1]),
    DirectionEnum.RIGHT: np.array([1, 0]),
    DirectionEnum.DOWN: np.array([0, 1]),
    DirectionEnum.LEFT: np.array([-1, 0]),
    DirectionEnum.INVALID: np.array([0, 0])
}

def get_vec_by_direction(_dir):
    assert isinstance(_dir, DirectionEnum)
    return Direction2Vec[_dir]


WEAPON_SLOT = 0
CLOTHES_SLOT = 1


class Player(GameItem):
    def __init__(self, env):
        super().__init__()
        self.id = next(player_id)
        self.env = env
        from player import PlayerLogic
        self._logic = PlayerLogic(self)
        self.action = None
        self.events = []
        self.ai_logic = None
        self.state = PlayerState.IDLE
        self.sub_state = None
        self.sub_state_stack = []           # used by mapcell logic, for resume pre sub_state when leave current cell
        self.interact_target = 0
        self.friend_ship: Dict[int, int] = {}       # npc id 2 friendship value
        self.handy_items: List[Tuple[object, int]] = [(None, 0) for _ in range(5)] # items id 2 count, slot max size is 5
        self.home_items: List[Tuple[object, int]] = [(None, 0) for _ in range(5)] # items id 2 count , slot max size is 50
        self.equips = [None, None]                  # equip slots, two slot, one for weapon, one for clothes
        self.energy = 100
        self.hp_max = 100
        self.hunger = 10000
        self.hp = 50
        self.attack = 10
        self.attack_frame = 0                       # attack settlement frame
        self.collect_frame = 0
        self.position = np.array([0, 0])            # use numpy array to make compute handy
        self.direction = DirectionEnum.UP
        self.killer = None                          # who killed me
        self.active_message = []
        self.passive_message = []

    @property
    def speed(self):
        return self._logic.get_player_move_speed()

    def get_name(self):
        return "player_" + str(self.id)

    def update(self):
        if self._logic:
            self._logic.update()

    def is_dead(self):
        return self.hp <= 0

    def get_fells_temperature(self):
        return self._logic.get_fells_temperature()

    def can_damage_by(self, player):
        return self._logic.can_damage_by(player)

    def damage_by(self, attacker, damage):
        real_damage = self._logic.damage_by(attacker, damage)
        if self.passive_message is not None:
            self.passive_message.append(f'{self.get_name()} attacked by {attacker.get_name()} '
                                        f'damage {real_damage} {"dead" if self.is_dead() else ""}')
        return real_damage

    def find_interact_target(self):
        return self._logic.find_interact_target()

    def on_new_day(self):
        if hasattr(self._logic, "on_new_day"):
            self._logic.on_new_day()

    def un_equip(self, slot):
        self._logic.un_equip(slot)

    def use(self, handy_idx: int):
        self._logic.use(handy_idx)

    def drop(self, handy_idx: int):
        self._logic.drop(handy_idx)

    def make(self, item):
        self._logic.make(item)

    def pickup(self, items):
        self._logic.pickup(items)

    def rest(self):
        self._logic.rest()

    def trim_handy(self):
        pass

    def trim_house(self):
        pass

    def receive_event(self, event):
        assert isinstance(event, Event)
        self.events.append(event)

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        return None

    def __setitem__(self, name, value):
        setattr(self, name, value)

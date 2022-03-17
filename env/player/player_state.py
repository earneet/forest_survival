from enum import IntEnum

import enum
import numpy as np


class PlayerState(IntEnum):
    IDLE = 0  # 什么都没干
    MOVING = 1  # 在移动
    BATTLING = 2  # 在打架
    COLLECTING = 3  # 在收集
    RESTING = 4  # 在休整
    MAKING = 5  # 在制造


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

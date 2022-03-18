import enum

import numpy as np


@enum.unique
class DirectionEnum(enum.IntEnum):
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

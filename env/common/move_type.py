import enum


@enum.unique
class MoveType(enum.IntEnum):
    WALKING = 0
    RUNNING = 1
    SWIMMING = 2

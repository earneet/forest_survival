from enum import Enum

from engine import Engine
from env_logic import EnvLogic
from map import Map
from timer import TimerManager


class Season(Enum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4


SeasonTemperatures = {
    Season.SPRING: 25,
    Season.SUMMER: 30,
    Season.AUTUMN: 18,
    Season.WINTER: 10
}


class Direction(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4


Direction2Vec = {
    Direction.NORTH: (0, 1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, -1),
    Direction.WEST: (-1, 0)
}


def get_vec_by_direction(_dir):
    assert isinstance(_dir, Direction)
    return Direction2Vec[_dir]


class Env:
    STEP_FRAME_INTERVAL = 10
    STEP_BREAK = 1 / STEP_FRAME_INTERVAL
    HOUR_SECOND_RATIO = 24  # * 60 * 60
    DAY_HOUR_RATIO = 24
    MONTH_DAY_RATIO = 30
    SEASON_MONTH_RATIO = 3
    YEAR_SEASON_RATIO = 4

    def __init__(self, render: bool = False):
        self.engine = Engine()
        self.logic = EnvLogic(self)
        self.timer = TimerManager()
        self.render = render
        self.season = Season.SPRING
        self.animals = []
        self.players = []
        self.plants = []
        self.frames = 0
        self.map = None
        self.message = []

    def get_global_temperature(self):
        return SeasonTemperatures[self.season]

    def reset(self):
        self.engine.reset()
        self.frames = 0
        self.map = Map()
        self.logic.reset()

    def step(self, actions):
        assert actions is not None, "actions Can't be None"
        frames = 0
        while frames < self.STEP_FRAME_INTERVAL:
            self.logic.update()
            if self.render:
                self.engine.update()

    def observe(self):
        assert self is not None
        return ""

    def is_player(self, pid) -> bool:
        for p in self.players:
            if p.id == pid:
                return True
        return False

    def is_animal(self, aid) -> bool:
        for a in self.animals:
            if a.id == aid:
                return True
        return False

    def get_animal(self, aid):
        for a in self.animals:
            if a.id == aid:
                return a

    def get_player(self, pid):
        for p in self.players:
            if p.id == pid:
                return p


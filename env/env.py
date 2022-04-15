from enum import IntEnum

from .common.season import Season, get_season_temperature
from .engine import get_engine
from .entity import marshal
from .env_logic import EnvLogic
from .map import Map

class Env:
    STEP_FRAME_INTERVAL = 10
    STEP_BREAK = 1 / STEP_FRAME_INTERVAL
    HOUR_SECOND_RATIO = 2  # * 60 * 60
    DAY_HOUR_RATIO = 24
    MONTH_DAY_RATIO = 30
    SEASON_MONTH_RATIO = 3
    YEAR_SEASON_RATIO = 4

    def __init__(self, render: bool = False):
        self.logic = EnvLogic(self)
        self.render = render
        self.season = Season.SPRING
        self.animals = []
        self.players = []
        self.plants = []
        self.frames = 0
        self.map = None
        self.message = []
        self.engine = get_engine()
        self.engine.set_env(self)
        self.ai = "rule"

    def get_global_temperature(self):
        return get_season_temperature(self.season)

    def reset(self):
        self.frames = 0
        self.map = Map()
        self.logic.reset()
        if self.render:
            self.engine.set_env(self)
            self.engine.reset()

    def step(self, actions):
        assert actions is not None, "actions Can't be None"
        frames = 0
        while frames < self.STEP_FRAME_INTERVAL:
            self.logic.update()
            if self.render:
                self.engine.update()
            frames += 1

    def observe(self):
        assert self is not None
        for p in self.players:
            p.active_message = []
            p.passive_message = []
        self.message = []
        return marshal(self)

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

    def marshal(self):
        pass

    def marshal_animal(self, animal):
        pass

    def marshal_plants(self, plant):
        pass

    def marshal_player(self, player):
        pass

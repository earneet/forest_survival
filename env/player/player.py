from enum import Enum
from typing import Dict

from env.engine.gameitem import GameItem
import itertools
import numpy as np

from player import PlayerLogic

player_id = itertools.count()
next(player_id)


class PlayerState(Enum):
    IDLE = 0
    MOVING = 1
    BATTLING = 2
    COLLECTING = 3
    RESTING = 4
    MAKING = 5


class MoveType(Enum):
    WALKING = 0
    RUNNING = 1
    SWIMMING = 2


class SlotType(Enum):
    EQUIP = 0
    CLOTH = 1


class Player(GameItem):
    def __init__(self, env):
        super().__init__()
        self.id = next(player_id)
        self.env = env
        self._logic = PlayerLogic(self)
        self.action = None
        self.events = []
        self.ai_logic = None
        self.state = PlayerState.IDLE
        self.sub_state = None
        self.interact_target = 0
        self.friend_ship: Dict[int, int] = {}   # npc id 2 friendship value
        self.handy_items: Dict[int, int] = {}  # items id 2 count, slot max size is 5
        self.home_items: Dict[int, int] = {}    # items id 2 count , slot max size is 50
        self.equips = [None, None]  # equip slots, two slot, one for weapon, one for clothes
        self.energy = 100
        self.hp_max = 100
        self.hp = 100
        self.attack = 10
        self.attack_frame = 0           # attack settlement frame
        self.hunger = 10
        self.position = np.array([0, 0])    # use numpy array to make compute handy
        self.direction = np.array([(1, 0)])
        self.speed = 0

    def get_player_name(self):
        return "player_" + str(self.id)

    def update(self):
        if self._logic:
            self._logic.update()

    def on_new_day(self):
        if hasattr(self._logic, "on_new_day"):
            self._logic.on_new_day()

    def equip(self, item_id, slot=SlotType.EQUIP):
        self._logic.equip(item_id, slot)

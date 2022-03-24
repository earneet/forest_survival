from typing import Dict, List, Tuple

import itertools
import numpy as np

from env.common.event.event import Event
from env.items import is_food
from env.player.player_config import player_cfg
from env.player.player_logic import PlayerLogic
from env.common import PlayerState, DirectionEnum

player_id = itertools.count()
next(player_id)

_Cosumeable_Items = Tuple[int, str, int]


class Player:
    def __init__(self, env):
        self.id = next(player_id)
        self.env = env
        self._logic = PlayerLogic(self)
        self.action = None
        self.events = []
        self.state = PlayerState.IDLE
        self.sub_state = None
        self.sub_state_stack = []  # used by mapcell logic, for resume pre sub_state when leave current cell
        self.interact_target = 0
        self.friend_ship: Dict[int, int] = {}  # npc id 2 friendship value
        self.handy_items: List[Tuple[object, int]] = [(None, 0) for _ in
                                                      range(5)]  # items id 2 count, slot max size is 5
        self.home_items: List[Tuple[object, int]] = [(None, 0) for _ in
                                                     range(5)]  # items id 2 count , slot max size is 50
        self.equips = [None, None]  # equip slots, two slot, one for weapon, one for clothes
        self.energy = player_cfg.energy_init or player_cfg.energy_max
        self.energy_max = player_cfg.energy_max
        self.hunger = player_cfg.hunger_init or player_cfg.hunger_max
        self.hunger_max = player_cfg.hunger_max
        self.hp = player_cfg.hp_init
        self.hp_max = player_cfg.hp_max
        self.attack = player_cfg.attack
        self.attack_range = int(player_cfg.attack_range)
        self.attack_frame = 0  # attack settlement frame
        self.make_frame = 0  # making settlement frame
        self.collect_frame = 0
        self.position = np.array([0, 0])  # use numpy array to make compute handy
        self.direction = DirectionEnum.UP
        self.killer = None  # who killed me
        self.active_message = []
        self.passive_message = []
        self.is_player = True
        self.is_animal = False
        self.is_plant = False

    @property
    def speed(self):
        return self._logic.get_player_move_speed()

    @property
    def frames(self):
        return self.env.frames if self.env else 0

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

    def find_interact_target(self, interact_type="collecting"):
        return self._logic.find_interact_target(interact_type)

    def find_interact_target_insight(self, interact_type="collecting"):
        return self._logic.find_interact_target_insight(interact_type)

    def on_new_day(self):
        if hasattr(self._logic, "on_new_day"):
            self._logic.on_new_day()

    def handy2home(self, idx):
        return self._logic.handy2home(idx)

    def home2handy(self, idx):
        return self._logic.home2handy(idx)

    def in_home(self):
        return self._logic.in_home()

    def move_home(self):
        return self._logic.move_home()

    def un_equip(self, slot):
        self._logic.un_equip(slot)

    def use(self, handy_idx: int):
        self._logic.use(handy_idx)

    def drop(self, handy_idx: int):
        self._logic.drop(handy_idx)

    def make(self, item):
        if item:
            self._logic.make(item)

    def pickup(self, items, home_box=True):
        self._logic.pickup(items, home_box)

    def rest(self):
        self._logic.rest()

    def collect(self):
        self._logic.collect()

    def trim_handy(self):
        # todo trim handy items
        pass

    def trim_house(self):
        # todo trim house items
        pass

    def receive_event(self, event):
        assert isinstance(event, Event)
        self.events.append(event)

    def get_food_cnt(self, handy=True) -> int:
        total_cnt = 0
        container = self.handy_items if handy else self.home_items
        for item, cnt in container:
            if item and is_food(item):
                total_cnt += cnt
        return total_cnt

    def get_foods(self, handy=True) -> List[_Cosumeable_Items]:
        foods = []
        container = self.handy_items if handy else self.home_items
        for idx, item, cnt in enumerate(container):
            if is_food(item):
                foods.append((idx, item, cnt))
        return foods

    def __getitem__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        return None

    def __setitem__(self, name, value):
        setattr(self, name, value)

import logging
import math
from collections import defaultdict
from typing import Union, List

import numpy as np

from env.AI.path import find_path
from env.animals import Animal
from env.common.event.event import *
from env.items.item import Equip, Cloth, make_equip, make_cloth
from env.common import Terrain, MoveType, PlayerState, SlotType, CLOTHES_SLOT
from env.plants import Plant
from env.player.logic.concretelogic import PlayerMoveLogic, PlayerBattleLogic, PlayerMakeLogic, PlayerCollectLogic, \
    PlayerRestingLogic, PlayerIdleLogic
from env.player.logic.player_common_logic import check_materials


class PlayerLogic:
    MOVETYPE2HUNGERCOST = defaultdict(int)
    MOVETYPE2HUNGERCOST.update({
        MoveType.WALKING: 5,
        MoveType.RUNNING: 10,
        MoveType.SWIMMING: 8
    })

    def __init__(self, player):
        self.player = player
        self.move_logic = PlayerMoveLogic(player, self)
        self.battle_logic = PlayerBattleLogic(player, self)
        self.make_logic = PlayerMakeLogic(player, self)
        self.collect_logic = PlayerCollectLogic(player, self)
        self.rest_logic = PlayerRestingLogic(player, self)
        self.idle_logic = PlayerIdleLogic(player, self)
        self.cur_logic = None

    def update(self):
        player = self.player
        if player.hp <= 0:
            return self.dead_update()
        state, sub_state = player.state, player.sub_state
        if self.cur_logic:
            self.cur_logic.update()
        else:
            pass

        self._process_natural_energy_cost(state, sub_state)
        self._process_natural_hunger_cost(state, sub_state)
        self._process_natural_recover()
        self._process_equip_cost()

        self.player.hp = min(self.player.hp, self.player.hp_max)  # 如果hp有溢出，则在最后的逻辑中移除溢出
        self.player.hp = max(self.player.hp, 0)
        self.player.hunger = min(self.player.hunger, self.player.hunger_max)
        self.player.hunger = max(self.player.hunger, 0)
        self.player.energy = min(self.player.energy, self.player.energy_max)
        self.player.energy = max(self.player.energy, 0)

        self._process_new_event()

    def switch_state(self, new_state, *args):
        """
        this is an unenabled state switch function

        Args:
            new_state: new state logic object
            *args:  additional args

        Returns:

        """
        if self.cur_logic:
            self.cur_logic.on_leave_state()
        if new_state.can_enter_state():
            self.cur_logic = new_state
            self.cur_logic.on_enter_state(*args)

    def dead_update(self):
        pass

    def get_fells_temperature(self):
        return self.get_naked_temperature() + self.get_cloth_delta_temperature()

    def get_naked_temperature(self):
        return self.player.env.get_global_temperature() + self.get_terrain_delta_temperature()

    def get_terrain_delta_temperature(self):
        cell = self.player.env.map.get_cell_by_pos(self.player.position)
        return cell.get_temperature_delta()

    def get_cloth_delta_temperature(self):
        equipment = self.player.equips[CLOTHES_SLOT]
        equipment_delta = 0 if not equipment else equipment.get_temperature_delta()
        return equipment_delta

    def can_damage_by(self, attacker):
        return self.battle_logic.can_damage_by(attacker)

    def damage_by(self, attacker, damage):
        return self.battle_logic.damage_by(attacker, damage)

    def rest(self):
        cell = self.player.env.map.get_cell_by_pos(self.player.position)
        if cell and cell.type == Terrain.SELF_HOUSE:
            self.switch_state(self.rest_logic)
            return True
        return False

    def un_equip(self, slot):
        assert 0 <= slot < 2
        equip = self.player.equips[slot]
        if equip is None:
            return
        self.put_handy(equip, 1)
        self.player.equips[slot] = None

    def equip(self, item_idx) -> bool:
        assert 0 <= item_idx < 5, "item_idx invalid"
        handy_item = self.player.handy_items[item_idx]
        if handy_item[0] is None or handy_item[1] == 0:
            logging.warning("no such item to equip")
            return False

        slot = int(SlotType.EQUIP) if isinstance(handy_item[0], Equip) else int(SlotType.CLOTH)

        old = self.player.equips[slot]
        self.player.equips[slot] = handy_item[0]
        if old:
            self.player.handy_items[item_idx] = (old, 1)
        else:
            self.player.handy_items[item_idx] = (None, 0)

    def use(self, item_idx):
        handy_item = self.player.handy_items[item_idx]
        item, cnt = handy_item[0], handy_item[1]
        if cnt <= 0:
            msg = f"try to use item at {item_idx} but there is no item"
            logging.warning(msg)
            self.player.active_message.append(msg)
            return False
        if isinstance(item, (Equip, Cloth)):
            return self.equip(item_idx)

        from env.items import prop_cfg
        item_cfg = prop_cfg[item]
        if not item_cfg.usable:
            msg = f" item {item} is not usable"
            logging.warning(msg)
            self.player.active_message.append(msg)
            return False

        tips = f"player {self.player.get_name()} use item {item} "
        for effect in item_cfg.effect:
            self.player[effect] += item_cfg.effect[effect]
            tips += effect + " " + str(item_cfg.effect[effect]) + " "
        self.player.handy_items[item_idx] = (item, cnt - 1) if cnt > 1 else (None, 0)
        self.player.active_message.append(tips)
        return True

    def drop(self, item_idx):
        handy_item = self.player.handy_items[item_idx]
        item, cnt = handy_item[0], handy_item[1]
        if item is None or cnt <= 0:
            logging.warning("there is no item to drop")
            return
        cnt -= 1
        self.player.handy_items[item_idx] = (item, cnt) if cnt > 1 else (None, 0)

    def find_interact_target(self, interact="collecting") -> Union[Animal, Plant]:
        self_pos = self.player.position
        round_cells = self.player.env.map.get_round_cells_by_pos(self_pos)
        interactive = self._find_interact_target_in_cells(round_cells, interact)
        interactive.sort(key=lambda x: np.linalg.norm(x.position - self_pos))
        return interactive[0] if interactive and np.linalg.norm(
            interactive[0].position - self_pos) <= self.player.attack_range else None

    def find_interact_target_insight(self, interact="collecting") -> List[Union[Animal, Plant]]:
        world_map = self.player.env.map
        ken, self_pos = self.player.ken, self.player.position
        cell_range = math.ceil(ken / world_map.cell_size)
        round_cells = world_map.get_round_cells_by_pos(self_pos, cell_range)
        interactive = self._find_interact_target_in_cells(round_cells, interact)
        return list(filter(lambda x: np.linalg.norm(x.position - self_pos) <= ken, interactive))

    def _find_interact_target_in_cells(self, cells, interact="collecting") -> List[Union[Animal, Plant]]:
        interactive = []
        for cell in cells:
            if interact == "collecting":
                interactive.extend(filter(lambda x: not x.is_dead(), cell.plants))
            elif interact == "batting":
                interactive.extend(cell.animals)
                interactive.extend(filter(lambda x: x != self.player and not x.is_dead(), cell.players))
        return interactive

    def pickup(self, items, home_box=True):
        for item, cnt in items.items():
            if item.endswith("_equip"):
                for i in range(cnt):
                    production = make_equip(item)
                    self.put_handy(production, home_box)
            elif item.endswith("_clothes"):
                for i in range(cnt):
                    production = make_cloth(item)
                    self.put_handy(production, home_box)
            else:
                self.put_handy(item, cnt, home_box)

    def make(self, item) -> bool:
        assert isinstance(item, str)
        cfgs = None
        if item.endswith("_clothes"):
            from env.items import clothes_cfg
            cfgs = clothes_cfg
        elif item.endswith("_equip"):
            from env.items import equip_cfg
            cfgs = equip_cfg
        cfg = cfgs[item]
        if cfg.recipe is None or not check_materials(self.player, cfg.recipe.materials):
            logging.warning(f"have no enough materials for make a {item}")
            self.player.active_message.append(
                f"try to make a {item} but have no enough materials for make a {item}")
            return False
        elif not self._check_handy_space(1):
            logging.warning(f"have no enough bag space for make a {item}")
            self.player.active_message.append(
                f"try to make a {item} but have no enough bag space for make a {item}")
            return False
        self.switch_state(self.make_logic)
        return True  # all other prop don't need to be make

    def get_player_move_speed(self):
        return self.move_logic.get_move_speed()

    def _check_handy_space(self, n):
        for item in self.player.handy_items:
            if item[0] is None or item[1] == 0:
                n -= 1
        return n <= 0

    def remove_cost(self, materials) -> bool:
        cost = {}
        for name, cnt in materials.items():
            keep = []
            for i in range(len(self.player.handy_items)):
                item = self.player.handy_items[i]
                if item[0] == name or isinstance(item[0], (Equip, Cloth)) and item[0].name() == name:  # common item
                    keep.append((i, item[1]))
            keep.sort(key=lambda x: x[1])
            remain = cnt
            for item in keep:
                diff = item[1] if item[1] < remain else remain
                remain -= diff
                cost[item[0]] = diff
                if remain == 0:
                    break
            else:
                return False
        for idx, cnt in cost.items():
            item = self.player.handy_items[idx]
            self.player.handy_items[idx] = (None, 0) if item[1] <= cnt else (item[0], item[1] - cnt)
        return True

    def put_handy(self, item, cnt=1, home_box=True) -> bool:
        if cnt == 0:
            return True
        assert cnt > 0, "cnt must greate than 0"
        if isinstance(item, str):
            return self._put_common(item, cnt, home_box)
        if isinstance(item, Equip) or isinstance(item, Cloth):
            return self._put_unique(item, home_box)

    def home2handy(self, idx) -> bool:
        assert 0 <= idx < len(self.player.home_items), "idx out of bounds"
        if not self._check_home():
            logging.warning("This op must in home")
            return False
        prop, cnt = self.player.home_items[idx]
        if prop is None or cnt == 0:
            logging.warning(f"home box idx {idx} have no item")
            return False
        put_success = False
        if isinstance(prop, str):
            put_success = self._put_common(prop, 1)
        elif isinstance(prop, (Equip, Cloth)):
            put_success = self._put_unique(prop)
        if not put_success:
            logging.warning(f"handy bag full")
            return False
        cnt -= 1
        self.player.home_items[idx] = (None, 0) if cnt == 0 else (prop, cnt)
        return True

    def handy2home(self, idx) -> bool:
        if not self._check_home():
            logging.warning("This op must in home")
            return False

        assert 0 <= idx < len(self.player.handy_items), "idx out of bounds"
        if not self._check_home():
            return False
        prop, cnt = self.player.handy_items[idx]
        if prop is None or cnt == 0:
            logging.warning(f"home box idx {idx} have no item")
            return False
        put_success = False
        if isinstance(prop, str):
            put_success = self._put_common(prop, 1, False)
        elif isinstance(prop, (Equip, Cloth)):
            put_success = self._put_unique(prop, False)
        if not put_success:
            logging.warning(f"handy bag full")
            return False
        cnt -= 1
        self.player.handy_items[idx] = (None, 0) if cnt == 0 else (prop, cnt)
        return True

    def in_home(self):
        return self._check_home()

    def move_home(self):
        home_position = self.player.home_position()
        return self.move_to(home_position)

    def move_to(self, position):
        self.switch_state(self.move_logic, position)

    def _check_home(self) -> bool:
        env_map = self.player.env.map
        cell = env_map.get_cell_by_pos(self.player.position)
        return cell.type == Terrain.SELF_HOUSE

    def _put_common(self, item_name, cnt, home_box=True) -> bool:
        remain = cnt
        # first pile up to save space
        handy_items = self.player.handy_items if home_box else self.player.home_items
        for i in range(len(handy_items)):
            zone = handy_items[i]
            if zone[0] == item_name:
                capacity = 99 - zone[1]
                putin_num = min(cnt, capacity)
                item = (zone[0], zone[1] + putin_num)
                handy_items[i] = item
                remain -= putin_num
                logging.info(f" put {item_name} count {putin_num}")
                if remain == 0:
                    return True

        # if any remain, put them a new zone
        while remain > 0:
            for i in range(len(handy_items)):
                zone = handy_items[i]
                if zone[0] is None or zone[1] == 0:
                    putin_num = min(99, remain)
                    item = (item_name, putin_num)
                    handy_items[i] = item
                    remain -= putin_num
                    logging.info(f" put {item_name} count {putin_num}")
                    if remain == 0:
                        return True

    def _put_unique(self, item, home_box=True) -> bool:
        handy_items = self.player.handy_items if home_box else self.player.home_items
        for i in range(len(handy_items)):
            zone = handy_items[i]
            if zone[0] is None or zone[1] == 0:
                handy_items[i] = (item, 1)
                return True
        return False

    def _process_new_event(self):
        while self.player.events:
            event = self.player.events.pop(0)
            if isinstance(event, StopMove):
                self.move_logic.process_event_stop(event)
            elif isinstance(event, (MoveUp, MoveLeft, MoveDown, MoveRight)):
                self.move_logic.process_event_move(event)
            elif isinstance(event, Attack):
                self.battle_logic.process_event_attack(event)
            elif isinstance(event, (Collecting, CollectEnd)):
                self._process_event_collecting(event)
            elif isinstance(event, Resting):
                self.player.rest()
            elif isinstance(event, UseItem):
                self.player.use(event.idx)
            elif isinstance(event, DropItem):
                self.player.drop(event.idx)
            elif isinstance(event, MakeItem):
                self.player.make(event.item)
            elif isinstance(event, UnEquip):
                self.player.un_equip(event.idx)
            elif isinstance(event, Exchange):
                if event.dir:
                    self.player.home2handy(event.idx)
                else:
                    self.player.handy2home(event.idx)

    def battle(self):
        target = self.player.find_interact_target("batting")
        if target:
            self.switch_state(self.battle_logic, target)

    def collect(self):
        if self.player.state == PlayerState.COLLECTING:
            return
        target = self.player.find_interact_target()
        if not target:  # can't find any collectable target
            logging.warning("can't find any collectable target")
            return
        self.switch_state(self.collect_logic, target)

    def _process_event_collecting(self, event: Collecting):
        if isinstance(event, Collecting):
            self.collect()
        elif isinstance(event, CollectEnd):
            self.switch_state(self.idle_logic)

    def _process_natural_recover(self):
        hunger = self.player.hunger
        energy = self.player.energy
        temperature = self.player.get_fells_temperature()
        hp = self.player.hp
        if hunger > 80 and energy > 80 and (18 <= temperature <= 30) and hp > 0:
            self.player.hp += 5 * self.player.env.STEP_BREAK

        if self.player.state == PlayerState.RESTING:
            self.player.energy += 20 * self.player.env.STEP_BREAK

    def _process_natural_energy_cost(self, state, _):
        env = self.player.env
        energy_cost = 0
        if state == PlayerState.RESTING:
            pass
        elif state == PlayerState.BATTLING or PlayerState.COLLECTING or PlayerState.MAKING:
            energy_cost += 10 / env.STEP_FRAME_INTERVAL * env.HOUR_SECOND_RATIO
        else:
            energy_cost += 5 / env.STEP_FRAME_INTERVAL * env.HOUR_SECOND_RATIO

        fells_temperature = self.get_fells_temperature()
        if fells_temperature >= 30:
            energy_cost *= 2  # fells_temperature >= 30°， energy cost twice
        self.player.energy -= energy_cost
        if self.player.energy < 0:
            self.player.energy = 0

    def _process_natural_hunger_cost(self, state, sub_state):
        player, env = self.player, self.player.env
        cost = 1
        if state == PlayerState.MOVING:
            cost += self.MOVETYPE2HUNGERCOST[sub_state]
        elif state == PlayerState.BATTLING:
            cost += 1
        self.player.hunger -= cost * env.STEP_BREAK
        if player.hunger <= 0:
            player.hunger = 0
            player.hp = 0

    def _process_equip_cost(self):
        player, env = self.player, self.player.env
        for i in range(len(player.equips)):
            equip = player.equips[i]
            if equip is None:
                continue
            equip.wear -= 1 * env.STEP_BREAK
            if equip.wear <= 0:
                player.equips[i] = None

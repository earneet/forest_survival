import logging
from collections import defaultdict

import numpy as np

from event import StopMove, MoveDown, MoveUp, MoveLeft, MoveRight, Attack, Collecting, Resting, CollectEnd, UseItem, \
    DropItem, MakeItem, UnEquip, Exchange
from items.item import Equip, Cloth, make_equip, make_cloth
from map import Terrain
from .player import MoveType, PlayerState, SlotType, get_vec_by_direction


class PlayerMoveLogic:
    def __init__(self, player, logic):
        self.player = player
        self.owner_logic = logic

    def on_enter_state(self, *args):
        pass

    def on_leave_state(self, *_):
        self.player.state = PlayerState.IDLE
        self.player.sub_state = None
        self.owner_logic.cur_logic = None

    def update(self):
        player = self.player
        env = player.env
        speed = self.get_player_move_speed()
        cur_pos = player.position
        tar_pos = speed * get_vec_by_direction(player.direction) + cur_pos
        cur_cell = env.map.get_cell_by_pos(cur_pos)
        tar_cell = env.map.get_cell_by_pos(tar_pos)
        if not tar_cell.player_can_move_in(player):
            self._move_to_edge(cur_cell)
            from player import PlayerState
            player.state = PlayerState.IDLE
            player.sub_state = None
            return
        player.position = tar_pos
        cur_cell.player_move_out(player)
        tar_cell.player_move_in(player)

    def get_player_move_speed(self):
        player = self.player
        env = player.env
        env.get_global_temperature()

        # move type speed
        from player import MoveType
        if player.sub_state == MoveType.WALKING:
            speed = 5 * env.STEP_BREAK
        elif player.sub_state == MoveType.RUNNING:
            speed = 8 * env.STEP_BREAK
        elif player.sub_state == MoveType.SWIMMING:
            speed = 3 * env.STEP_BREAK
        else:
            return 0

        # hunger effect
        if self.player.hunger < 5:
            speed = 0
        elif 5 <= self.player.hunger < 20:
            speed *= 0.5
        elif 20 <= self.player.hunger < 60:
            pass
        elif 60 <= self.player.hunger < 90:
            speed *= 1.2
        elif 90 <= self.player.hunger <= 100:
            speed *= 1.5
        return speed

    def process_event_stop(self, _):
        if self.player.state != PlayerState.MOVING:
            return
        self.on_leave_state()

    def process_event_move(self, event):
        from player.player import DirectionEnum
        if self.player.state != PlayerState.MOVING:
            cell = self.player.env.map.get_cell_by_pos(self.player.position)
            self.owner_logic.on_leave_old_state()
            self.player.state = PlayerState.MOVING
            self.player.sub_state = MoveType.RUNNING
            self.owner_logic.cur_logic = self
            if hasattr(cell, "on_player_start_move"):
                cell.on_player_start_move()

        if isinstance(event, MoveUp):
            self.player.direction = DirectionEnum.UP
        elif isinstance(event, MoveRight):
            self.player.direction = DirectionEnum.RIGHT
        elif isinstance(event, MoveDown):
            self.player.direction = DirectionEnum.DOWN
        elif isinstance(event, MoveLeft):
            self.player.direction = DirectionEnum.LEFT
        else:
            assert False, "invalid move event"

    def _move_to_edge(self, cell):
        player = self.player
        left, right, bottom, top = player.env.map.get_cell_edge(cell)
        direction = player.direction
        from player.player import DirectionEnum
        pos = player.position
        if direction == DirectionEnum.UP:
            pos[1] = top
        elif direction == DirectionEnum.RIGHT:
            pos[0] = right
        elif direction == DirectionEnum.DOWN:
            pos[1] = bottom
        elif direction == DirectionEnum.LEFT:
            pos[0] = left
        player.position = pos


class PlayerBattleLogic:
    def __init__(self, player, logic):
        self.player = player
        self.owner_logic = logic

    def on_enter_state(self, *_):
        self.player.attack_frame = self.player.env.frames
        self.owner_logic.cur_logic = self

    def on_leave_state(self, *_):
        self.player.interact_target = None

    def update(self):
        player = self.player
        env = player.env
        last_settlement = player.attack_frame
        if env.frames - last_settlement != env.STEP_FRAME_INTERVAL:  # settlement battle per second
            return
        player.attack_frame = env.frames
        target = player.interact_target

        if target and not target.is_dead() and target.can_damage_by(player):
            damage = self._compute_attack()
            target.damage_by(player, damage)
            player.hunger -= 1  # 战斗状态下， 每次攻击 饱食度额外减一

        if not target or target.is_dead():
            self.on_leave_state()
            self.player.state = PlayerState.IDLE
            self.player.interact_target = None

            if target:
                if target.is_player:
                    pass
                elif target.is_animal:
                    rewards = target.drop()
                    self.player.pickup(rewards)

    def process_event_attack(self, _):
        if self.player.state == PlayerState.BATTLING:
            return
        target = self.player.find_interact_target("batting")
        if target is None:
            logging.warning("no interactive target found")
            return
        self.owner_logic.on_leave_old_state()
        self.player.state = PlayerState.BATTLING
        self.player.attack_frame = self.player.env.frames
        self.player.interact_target = target
        self.on_enter_state()

    def can_damage_by(self, attacker):
        return self.player != attacker

    def damage_by(self, attacker, damage):
        player = self.player
        if player.hp <= 0:
            return 0
        real_damage = self._compute_damage(damage)
        player.hp -= real_damage
        if player.hp <= 0:
            player.killer = attacker
        return real_damage

    def _compute_attack(self, player=None):
        player = self.player if player is None else player
        attack = player.attack
        equip = player.equips[SlotType.EQUIP]
        if equip is not None:
            attack += equip.get_attack()
        if player.energy < 20:  # if energy below than 20, attack make half effect
            attack *= 0.5
        return attack

    @staticmethod
    def _compute_damage(damage):
        # todo damage may be offset by equipment and other factors, now no equip can counteract damage
        return damage


class PlayerMakeLogic:
    def __init__(self, player, logic):
        self.player = player
        self.owner_logic = logic
        self.making_cfg = None
        self.success_frame = None

    def update(self):
        frame = self.player.frames
        if frame < self.success_frame:
            return
        self._make(self.making_cfg.name, self.making_cfg)
        self.on_leave_state()
        return

    def on_enter_state(self, *args):
        self.player.make_frame = self.player.frames
        self.making_cfg = args[0]
        self.success_frame = int(
            self.making_cfg.recipe.time_consuming * self.player.env.HOUR_FRAMES) + self.player.frames
        self.player.state = PlayerState.MAKING

    def on_leave_state(self, *_):
        self.player.state = PlayerState.IDLE
        self.player.sub_state = None
        self.making_cfg = None
        self.owner_logic.cur_logic = None
        self.player.make_frame = 0

    def _make(self, item, cfg) -> bool:
        production = None
        if item.endswith("_clothes"):
            production = make_cloth(item)
        elif item.endswith("_equip"):
            production = make_equip(item)
        if production:
            self.owner_logic.remove_cost(cfg.recipe.materials)
            self.owner_logic.put_handy(production)
            return True
        return False


class PlayerRestingLogic:
    def __init__(self, player, logic):
        self.player = player
        self.owner_logic = logic

    def update(self):
        pass

    def on_enter_state(self, *args):
        pass

    def on_leave_state(self, *args):
        pass


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

        if player.ai_logic:
            player.ai_logic.update()
        self._process_new_event()

    def on_leave_old_state(self):
        state = self.player.state
        if self.cur_logic:
            self.cur_logic.on_enter_state()
            return
        if state == PlayerState.COLLECTING:
            self.player.interact_target = None
        elif state == PlayerState.MOVING:
            self.move_logic.on_leave_state()
        elif state == PlayerState.IDLE:
            pass

    def dead_update(self):
        pass

    def get_fells_temperature(self):
        return self.player.env.get_global_temperature() + self.get_delta_temperature()

    def get_delta_temperature(self):
        cell = self.player.env.map.get_cell_by_pos(self.player.position)
        terrain_delta = cell.get_temperature_delta()
        from player import CLOTHES_SLOT
        equipment = self.player.equips[CLOTHES_SLOT]
        equipment_delta = 0 if not equipment else equipment.get_temperature_delta()
        return terrain_delta + equipment_delta

    def can_damage_by(self, attacker):
        return self.battle_logic.can_damage_by(attacker)

    def damage_by(self, attacker, damage):
        return self.battle_logic.damage_by(attacker, damage)

    def rest(self):
        cell = self.player.env.map.get_cell_by_pos(self.player.position)
        if cell and cell.type == Terrain.SELF_HOUSE:
            self.on_leave_old_state()
            self.player.state = PlayerState.RESTING
            self.player.sub_state = None
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
            # todo show error message box
            msg = f"try to use item at {item_idx} but there is no item"
            logging.warning(msg)
            self.player.active_message.append(msg)
            return False
        if isinstance(item, (Equip, Cloth)):
            return self.equip(item_idx)

        from items import prop_cfg
        item_cfg = prop_cfg[item]
        if not item_cfg.usable:
            # todo show error message box
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
            return
        cnt -= 1
        self.player.handy_items[item_idx] = (item, cnt - 1) if cnt > 1 else (None, 0)

    def find_interact_target(self, interact="collecting"):
        round_cells = self.player.env.map.get_round_cells_by_pos(self.player.position)
        interactables = []
        for cell in round_cells:
            if interact == "collecting":
                interactables.extend(cell.plants)
            elif interact == "batting":
                interactables.extend(cell.animals)
                interactables.extend(filter(lambda x: x != self.player, cell.players))
        self_pos = self.player.position
        interactables.sort(key=lambda x: np.linalg.norm(x.position - self_pos))
        return interactables[0] if interactables else None

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
            from items import clothes_cfg
            cfgs = clothes_cfg
        elif item.endswith("_equip"):
            from items import equip_cfg
            cfgs = equip_cfg
        cfg = cfgs[item]
        if cfg.recipe is None or not self._check_material(cfg.recipe.materials):
            logging.warning(f"have no enough materials for make a {item}")
            self.player.active_message.append(
                f"try to make a {item} but have no enough materials for make a {item}")
            return False
        elif not self._check_handy_space(1):
            logging.warning(f"have no enough bag space for make a {item}")
            self.player.active_message.append(
                f"try to make a {item} but have no enough bag space for make a {item}")
            return False
        self.on_leave_old_state()
        self.cur_logic = self.make_logic
        self.cur_logic.on_enter_state(cfg)
        return True  # all other prop don't need be make

    def get_player_move_speed(self):
        return self.move_logic.get_player_move_speed()

    def _check_handy_space(self, n):
        for item in self.player.handy_items:
            if item[0] is None or item[1] == 0:
                n -= 1
        return n <= 0

    def _check_material(self, materials) -> bool:
        haven = {}
        for s, cnt in self.player.handy_items:
            if s is None or cnt == 0:
                continue
            if not isinstance(s, str):
                s = s.name()
            if s not in haven:
                haven[s] = cnt
            else:
                haven[s] += cnt
        for name, cnt in materials.items():
            if name not in haven or cnt > haven[name]:
                return False
        return True

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

    def _check_home(self) -> bool:
        env_map = self.player.env.map
        cell = env_map.get_cell_by_pos(self.player.position)
        return cell.type == Terrain.SELF_HOUSE

    def _put_common(self, item, cnt, home_box=True) -> bool:
        remain = cnt
        # first pile up to save space
        handy_items = self.player.handy_items if home_box else self.player.home_items
        for i in range(len(handy_items)):
            zone = handy_items[i]
            if zone[0] == item:
                capacity = 99 - zone[1]
                putin_num = min(cnt, capacity)
                newzone = (zone[0], zone[1] + putin_num)
                handy_items[i] = newzone
                remain -= putin_num
                logging.info(f" put {item} count {putin_num}")
                if remain == 0:
                    return True

        # if any remain, put them a new zone
        while remain > 0:
            for i in range(len(handy_items)):
                zone = handy_items[i]
                if zone[0] is None or zone[1] == 0:
                    putin_num = min(99, remain)
                    newzone = (item, putin_num)
                    handy_items[i] = newzone
                    remain -= putin_num
                    logging.info(f" put {item} count {putin_num}")
                    if remain == 0:
                        return True

    def _put_unique(self, item, home_box=True) -> bool:
        handy_items = self.player.handy_items if home_box else self.player.home_items
        for i in range(len(handy_items)):
            zone = handy_items[i]
            if zone[0] is None or zone[1] == 0:
                newzone = (item, 1)
                handy_items[i] = newzone
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

    def collect(self):
        target = self.player.find_interact_target()
        if not target:  # can't find any collectable target
            logging.warning("can't find any collectable target")
            return
        self.on_leave_old_state()
        target.collect(self.player)
        self.player.interact_target = target
        self.player.state = PlayerState.COLLECTING
        self.player.sub_state = None

    def _process_event_collecting(self, event: Collecting):
        if isinstance(event, Collecting):
            self.collect()
        elif isinstance(event, CollectEnd):
            self.on_leave_old_state()
            self.player.state = PlayerState.IDLE
            self.player.sub_state = None

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
        from player import PlayerState
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
        from player import PlayerState
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

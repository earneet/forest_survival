import logging
from collections import defaultdict

from event import StopMove, MoveTop, MoveLeft, MoveRight, Attack, Collecting, Resting
from items.item import Equip, Cloth, make_equip
from .player import MoveType, PlayerState, SlotType


class PlayerMoveLogic:
    def __init__(self, player):
        self.player = player

    def get_player_move_speed(self):
        player = self.player
        env = player.env
        env.get_season_temperature()

        # move type speed
        speed = 1.0
        from player import MoveType
        if player.sub_state == MoveType.WALKING:
            speed = 5 * env.STEP_BREAK
        elif player.sub_state == MoveType.RUNNING:
            speed = 8 * env.STEP_BREAK
        elif player.sub_state == MoveType.SWIMMING:
            speed = 3 * env.STEP_BREAK
        else:
            # invalid state
            assert False, "invalid state"

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

    def update(self):
        player = self.player
        env = player.env
        speed = self.get_player_move_speed()
        cur_pos = player.position
        tar_pos = cur_pos + speed * player.direction
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

    def process_event_stop(self, event):
        if self.player.state == PlayerState.MOVING:
            pass
        pass

    def process_event_move(self, event):
        pass

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
    def __init__(self, player):
        self.player = player

    def update(self):
        player = self.player
        env = player.env
        last_settlement = player.attack_frame
        if last_settlement + env.frames != env.STEP_FRAME_INTERVAL:  # settlement battle per second
            return
        player.attack_frame = env.frames
        target = None
        if env.is_player(player.interact_target):
            target = env.get_player(player.interact_target)
        elif env.is_animal(player.interact_target):
            target = env.get_animal(player.interact_target)

        assert target is not None, f"player {player.id} battle with None "
        if not target.is_dead() and target.can_damage_by(player):
            damage = self._compute_attack()
            target.damage_by(player, damage)
        player.hunger -= 1  # 战斗状态下， 饱食度额外减一

    def process_event_attack(self, event):
        if self.player.state == PlayerState.BATTLING:
            return
        target = self.player.find_interact_target()
        if target is None:
            logging.warning("no interactive target found")
            return
        self.player.state = PlayerState.BATTLING
        self.player.attack_frame = self.player.env.frames
        self.player.interact_target = self.player.find_interact_target()

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
        if player.energy < 20:   # if energy below than 20, attack make half effect
            attack *= 0.5
        return attack

    def _compute_damage(self, damage):
        # todo damage may be offset by equipment and other factors, now no equip can counteract damage
        return damage


class MoveDown:
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
        self.move_logic = PlayerMoveLogic(player)
        self.battle_logic = PlayerBattleLogic(player)

    def update(self):
        logging.debug(f"player {self.player.id} update using default player update ... ")
        player = self.player
        if player.hp <= 0:
            return self.dead_update()
        env = player.env
        state, sub_state = player.state, player.sub_state
        from player import PlayerState
        if state == PlayerState.IDLE:
            pass
        elif state == PlayerState.MOVING:
            self.move_logic.update()
        elif state == PlayerState.BATTLING:
            self.battle_logic.update()
        elif state == PlayerState.COLLECTING:
            pass
        elif state == PlayerState.RESTING:
            pass
        else:
            pass

        self._process_natural_energy_cost(state, sub_state)
        self._process_natural_hunger_cost(state, sub_state)
        self._process_natural_recover()

        self.player.hp = min(self.player.hp, self.player.hp_max)    # 如果hp有溢出，则在最后的逻辑中移除溢出

        if player.ai_logic:
            player.ai_logic.update()
        self._process_new_event()

    def dead_update(self):
        pass

    def get_fells_temperature(self):
        return self.player.env.get_global_temperature() + self.get_delta_temperature()

    def get_delta_temperature(self):
        cell = self.player.map.get_cell_by_pos(self.player.position)
        terrain_delta = cell.get_temperature_delta()
        from player import CLOTHES_SLOT
        equipment = self.player.equips[CLOTHES_SLOT]
        equipment_delta = 0 if not equipment else equipment.get_temperature_delta()
        return terrain_delta + equipment_delta

    def equip(self, item_idx, slot) -> bool:
        assert 0 <= slot < 2, "slot invalid"
        assert 0 <= item_idx < 5, "item_idx invalid"
        handy_item = self.player.handy_items[item_idx]
        if slot == int(SlotType.EQUIP):
            if not isinstance(handy_item[0], Equip):
                # todo show error message box
                return False
        elif slot == int(SlotType.CLOTH):
            if not isinstance(handy_item[0], Cloth):
                # todo show error message box
                return False
        old = self.player.slots[slot]
        self.player.slots[slot] = handy_item[0]
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
            self.player.message.append(msg)
            return False
        if not isinstance(item, str):
            # todo show error message box
            msg = f" item {item_idx} is not a usable item"
            logging.warning(msg)
            self.player.message.append(msg)
            return False
        from items import prop_cfg
        item_cfg = prop_cfg[item]
        if not item_cfg.usable:
            # todo show error message box
            msg = f" item {item} is not usable"
            logging.warning(msg)
            self.player.message.append(msg)
            return False

        tips = f"player {self.player.get_name()} use item {item} "
        for effect in item_cfg.effect:
            self.player[effect] += item_cfg.effect[effect]
            tips += effect + " " + item_cfg.effect[effect] + " "
        self.player.handy_items[item_idx] = (item, cnt-1) if cnt > 1 else (None, 0)
        self.player.message.append(tips)
        return True

    def make(self, item) -> bool:
        assert isinstance(item, str)
        if item.endswith("_clothes"):
            return self._make_cloth(item)
        elif item.endswith("_equip"):
            return self._make_equip(item)
        return False    # all other prop don't need be make

    def _make_cloth(self, item) -> bool:
        from items import clothes_cfg
        if item not in clothes_cfg:
            logging.error(f"try to make a nonexistent cloth {item}")
            return False
        cfg = clothes_cfg[item]
        if not self._check_material(cfg.recipe.materials):
            logging.warning(f"have no enough materials for make a {item}")
            self.player.message.append(f"try to make a {item} but have no enough materials for make a {item}")
            # todo show a message box
            return False

        return False

    def _make_equip(self, item) -> bool:
        from items import equip_cfg
        if item not in equip_cfg:
            logging.error(f"try to make a nonexistent equip {item}")
            return False
        cfg = equip_cfg[item]
        if not self._check_material(cfg.recipe.materials):
            logging.warning(f"have no enough materials for make a {item}")
            self.player.message.append(f"try to make a {item} but have no enough materials for make a {item}")
            # todo show a message box
            return False
        make_equip(item)
        return False

    def _check_material(self, materials) -> bool:
        # todo implement check function
        return False

    def can_damage_by(self, attacker):
        return self.battle_logic.can_damage_by(attacker)

    def damage_by(self, attacker, damage):
        return self.battle_logic.damage_by(attacker, damage)

    def _process_new_event(self):
        while self.player.events:
            event = self.player.events.pop(0)
            if isinstance(event, StopMove):
                self.move_logic.process_event_stop(event)
            elif isinstance(event, (MoveTop, MoveLeft, MoveDown, MoveRight)):
                self.move_logic.process_event_move(event)
            elif isinstance(event, Attack):
                self.battle_logic.process_event_attack(event)
            elif isinstance(event, Collecting):
                pass
            elif isinstance(event, Resting):
                pass

    def _process_natural_recover(self):
        hunger = self.player.hunger
        energy = self.player.energy
        temperature = self.player.get_fells_temperature()
        hp = self.player.hp
        if hunger > 80 and energy > 80 and (18 <= temperature <= 30) and hp > 0:
            self.player.hp += 5 * self.player.env.STEP_BREAK

    def _process_natural_energy_cost(self, state, sub_state):
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
            energy_cost *= 2    # fells_temperature >= 30°， energy cost twice
        self.player.energy -= energy_cost

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


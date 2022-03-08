import logging
from collections import defaultdict

from player import MoveType


class PlayerMoveLogic:
    def __init__(self, player):
        self.player = player

    def get_player_move_speed(self):
        player = self.player
        env = player.env
        env.get_season_temperature()

        from player import MoveType
        if player.sub_state == MoveType.WALKING:
            return 5 * env.STEP_BREAK
        elif player.sub_state == MoveType.RUNNING:
            return 8 * env.STEP_BREAK
        elif player.sub_state == MoveType.SWIMMING:
            return 3 * env.STEP_BREAK
        else:
            # illegal state
            pass
        return 1.0

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
        if last_settlement + env.frames == env.STEP_FRAME_INTERVAL:  # settlement battle per second
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
        # todo damage may be offset by equipment and other factors
        return damage


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

    def equip(self, item_id, slot):
        if item_id == 0:
            self.player.equips[int(slot)] = None
        else:
            # todo equip equipment
            pass

    def can_damage_by(self, attacker):
        return self.battle_logic.can_damage_by(attacker)

    def damage_by(self, attacker, damage):
        return self.battle_logic.damage_by(attacker, damage)

    def _process_new_event(self):
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
        if state == PlayerState.RESTING:
            pass
        elif state == PlayerState.BATTLING or PlayerState.COLLECTING or PlayerState.MAKING:
            self.player.energy -= 10 / env.STEP_FRAME_INTERVAL * env.HOUR_SECOND_RATIO
        else:
            self.player.energy -= 5 / env.STEP_FRAME_INTERVAL * env.HOUR_SECOND_RATIO

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
            player.hp = 0  # todo trigger dead


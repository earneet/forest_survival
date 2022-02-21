import logging
import numpy as np


class PlayerMoveLogic:
    def __init__(self, player):
        self.player = player

    def get_player_move_speed(self):
        player = self.player
        env = player.env
        env.get_season_temperature()

        from player import MoveType
        if player.sub_state == MoveType.WALKING:
            pass
        elif player.sub_state == MoveType.RUNNING:
            pass
        elif player.sub_state == MoveType.SWIMMING:
            pass
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
            # todo move to edge
            from player import PlayerState
            player.state = PlayerState.IDLE
            player.sub_state = None
            return
        player.position = tar_pos
        cur_cell.player_move_out(player)
        tar_cell.player_move_in(player)


class PlayerLogic:
    def __init__(self, player):
        self.player = player
        self.move_logic = PlayerMoveLogic(player)

    def update(self):
        logging.debug(f"player {self.player.id} update using default player update ... ")
        player = self.player
        env = player.env
        state, sub_state = player.state, player.sub_state
        from player import PlayerState
        if state == PlayerState.IDLE:
            pass
        elif state == PlayerState.MOVING:
            self.move_logic.update()
        elif state == PlayerState.BATTLING:
            last_settlement = self.player.attack_frame
            if last_settlement + env.frames == env.FRAME_INTERVAL:      # settlement battle per second
                player.attack_frame = env.frames
                target = env.get_player(player.interact_target)
                assert target is not None, f"player {player.id} battle with None "
        elif state == PlayerState.COLLECTING:
            pass
        elif state == PlayerState.RESTING:
            pass
        else:
            pass
        self._process_natural_energy_cost(state, sub_state)
        self._process_natural_hunger_cost(state, sub_state)
        if player.ai_logic:
            player.ai_logic.update()
        self._process_new_event()

    def equip(self, item_id, slot):
        if item_id == 0:
            self.player.equips[int(slot)] = None
        else:
            # todo equip equipment
            pass

    def _compute_attack(self, player=None):
        player = self.player if player is None else player
        attack = player.attack
        if player.energy < 20:   # if energy below than 20, attack make half effect
            attack *= 0.5
        return attack

    def _process_new_event(self):
        pass

    def _process_natural_energy_cost(self, state, sub_state):
        env = self.player.env
        from player import PlayerState
        if state == PlayerState.RESTING:
            pass
        elif state == PlayerState.BATTLING or PlayerState.COLLECTING or PlayerState.MAKING:
            self.player.energy -= 10 / env.FRAME_INTERVAL * env.HOUR_SECOND_RATIO
        else:
            self.player.energy -= 5 / env.FRAME_INTERVAL * env.HOUR_SECOND_RATIO

    def _process_natural_hunger_cost(self, state, sub_state):
        env = self.player.env
        self.player.hunger -= 1 / env.FRAME_INTERVAL * env.HOUR_SECOND_RATIO


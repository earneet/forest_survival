import logging

from env.common import PlayerState, SlotType
from env.player.logic.concretelogic.concrete_logic import PlayerConcreteLogic


class PlayerBattleLogic(PlayerConcreteLogic):
    def __init__(self, player, logic):
        super(PlayerBattleLogic, self).__init__(player, logic)

    def on_enter_state(self, frames, target):
        self.player.attack_frame = frames
        self.player.interact_target = target

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
        if target is None or target.is_dead():
            logging.warning("no interactive target found")
            return
        self.parent_logic.switch_state(self, self.player.env.frames, target)

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

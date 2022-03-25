from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
import numpy as np


class Hunting(BaseSubGoal):
    def __init__(self):
        super(Hunting, self).__init__()

    def update(self, player) -> bool:
        target = player.find_interact_target(interact_type="batting")
        if not target:
            return False

        # todo Judge whether victory is possible
        distance = np.linalg.norm(player.position - target.position)
        if distance < player.get_attack_range():
            player.attack(target)
        else:
            player.move_to(target.position)
        return True

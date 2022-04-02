from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
import numpy as np


class CollectingFood(BaseSubGoal):
    def __init__(self):
        super(CollectingFood, self).__init__()

    def update(self, player) -> bool:
        targets = player.find_interact_target_insight(interact_type="collecting")
        target = player.find_interact_target(interact_type="collecting")
        if not target:
            return False

        # todo Judge whether victory is possible
        distance = np.linalg.norm(player.position - target.position)
        if distance < player.get_attack_range():
            player.collect()
        else:
            player.move_to(target.position)
        return True

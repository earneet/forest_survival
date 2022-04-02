import numpy as np
from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal


class CollectingHerb(BaseSubGoal):
    def __init__(self):
        super(CollectingHerb, self).__init__()

    def update(self, player) -> bool:
        plants = player.find_interact_target_insight(interact_type="collecting")
        self_pos = player.position
        herbs = list(filter(lambda x: x.get_name() == "herb_plant", plants))
        if not herbs:
            return False
        herbs.sort(key=lambda x: np.linalg.norm(x.position - self_pos))
        nearest = herbs[0]
        if np.linalg.norm(nearest.position - self_pos) < 1:
            player.collect()
        else:
            player.move_to(nearest.position)
        return True

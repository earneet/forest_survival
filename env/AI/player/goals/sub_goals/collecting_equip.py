from itertools import chain

import numpy as np

from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
from env.common import get_drop_equipment_beings


class CollectingEquip(BaseSubGoal):
    def __init__(self):
        super(CollectingEquip, self).__init__()

    def update(self, player) -> bool:
        self_pos = player.position
        living_beings_list = get_drop_equipment_beings()
        living_beings = list(filter(lambda x: x.get_name() in living_beings_list
                                    and np.linalg.norm(x.position - self_pos) <= player.ken,
                                    chain(player.env.animals, player.env.plants)))
        if not living_beings:
            return False
        living_beings.sort(key=lambda x: np.linalg.norm(x.position - self_pos))
        target = living_beings[0]
        if np.linalg.norm(target.position - self_pos) < player.get_attack_range():
            player.collect()
        else:
            player.move_to(target.position)
        return True

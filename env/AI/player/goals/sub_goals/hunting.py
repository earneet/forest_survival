from itertools import chain

from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
import numpy as np

from env.animals import Animal
from env.common import get_drop_food_beings, PlayerState


class Hunting(BaseSubGoal):
    def __init__(self):
        super(Hunting, self).__init__()

    def update(self, player) -> bool:
        self_pos = player.position
        candidates = get_drop_food_beings()
        living_beings = list(filter(lambda x: x.get_name() in candidates
                                    and np.linalg.norm(x.position - self_pos) <= player.ken,
                                    chain(player.env.animals, player.env.plants)))

        if not living_beings:
            return False

        living_beings.sort(key=lambda x: np.linalg.norm(x.position - self_pos))
        target = living_beings[0]
        if not target:
            return False

        if np.linalg.norm(target.position - self_pos) < player.get_attack_range():
            if isinstance(target, Animal):
                if player.state == PlayerState.BATTLING:
                    return True
                player.battle()
            else:
                if player.state == PlayerState.COLLECTING:
                    return True
                player.collect()
        else:
            player.move_to(target.position)

        return True

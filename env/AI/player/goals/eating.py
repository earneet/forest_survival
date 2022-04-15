from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.collecting_for_food import CollectingFood
from env.AI.player.goals.sub_goals.eating_handy import EatingHandy
from env.AI.player.goals.sub_goals.eating_home import EatingHome
from env.AI.player.goals.sub_goals.hunting import Hunting


class GoalEating(BaseGoal):
    def __init__(self):
        super(GoalEating, self).__init__()
        self.sub_goals = [EatingHandy(), EatingHome(), Hunting(), CollectingFood()]

    def match(self, player, cfg) -> bool:
        return cfg.hunger[0] <= player.hunger < cfg.hunger[1]

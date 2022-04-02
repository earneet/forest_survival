from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.eating_handy import EatingHandy
from env.AI.player.goals.sub_goals.eating_home import EatingHome
from env.AI.player.goals.sub_goals.hunting import Hunting
from env.common import Collecting


class GoalEating(BaseGoal):
    def __init__(self):
        super(GoalEating, self).__init__()
        self.sub_goals = [EatingHandy(), EatingHome(), Hunting(), Collecting()]

    def match(self, player, cfg) -> bool:
        return cfg.hunger[0] <= player.hunger < cfg.hunger[1]

    def update(self, player):
        for sg in self.sub_goals:
            if sg.update(player):
                return True
        return False

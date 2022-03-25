from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.eating_1 import SubGoalEating1
from env.AI.player.goals.sub_goals.eating_2 import SubGoalEating2
from env.AI.player.goals.sub_goals.hunting import Hunting
from env.common import Collecting


class GoalEating(BaseGoal):
    def __init__(self):
        super(GoalEating, self).__init__()
        self.sub_goals = [SubGoalEating1(), SubGoalEating2(), Hunting(), Collecting()]

    def update(self, player):
        for sg in self.sub_goals:
            if sg.update(player):
                return True
        return False

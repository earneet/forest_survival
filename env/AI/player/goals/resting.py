from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.gohome_rest import SubGoalGoHome


class RestGoal(BaseGoal):
    def __init__(self):
        super().__init__()
        self.sub_goals = [SubGoalGoHome()]

    def matched(self, player, cfg) -> bool:
        energy = player.energy
        return True

    def update(self, player):
        for sg in self.sub_goals:
            if sg.update(player):
                return True
        return False

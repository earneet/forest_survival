from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.gohome_rest import SubGoalGoHome


class RestGoal(BaseGoal):
    def __init__(self):
        super().__init__()
        self.sub_goals = [SubGoalGoHome()]

    def matched(self, player, cfg) -> bool:
        energy = player.energy
        if cfg.energy[0] > energy or energy > cfg.energy[1]:
            return False
        return True

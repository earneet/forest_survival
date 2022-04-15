from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal


class Idle(BaseSubGoal):
    def __init__(self):
        super(Idle, self).__init__()

    def update(self, player) -> bool:
        return True

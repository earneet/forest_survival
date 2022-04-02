from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal


class SubGoalGoHome(BaseSubGoal):
    def __init__(self):
        super(SubGoalGoHome, self).__init__()

    def update(self, player) -> bool:
        if player.in_home():
            player.rest()
            return True
        else:
            player.move_home()
            return True

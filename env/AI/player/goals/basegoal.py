import abc

class BaseGoal(abc.ABC):
    def __init__(self):
        self.sub_goals = []

    def match(self, player, cfg) -> bool:
        pass

    def update(self, player) -> bool:
        player.cur_sub_goal = ""
        for sg in self.sub_goals:
            if sg.update(player):
                player.cur_sub_goal = sg.__class__.__name__
                return True
        return False

import abc
import logging

from env.AI.player.goals.eating import GoalEating
from env.AI.player.goals.promote import PromoteGoal
from env.AI.player.goals.resting import RestGoal
from env.AI.player.goals.warming import WarmGoal


class Selector(abc.ABC):
    def __init__(self):
        pass

    def reset(self):
        pass

    def select(self, player):
        pass


class PlayerInnerSelector(Selector):
    goals = {
        "eating": GoalEating(),
        "warm": WarmGoal(),
        "rest": RestGoal(),
        "promote": PromoteGoal()}

    priority = ["eating", "warm", "rest", "promote"]

    def __init__(self, player, cfg):
        super(PlayerInnerSelector, self).__init__()
        self.cfg = cfg
        self.player = player
        self.idx = 0
        self.s_idx = 0

    def __iter__(self):
        for goal_cfg in self.cfg:
            for goal_name in self.priority:
                goal = self.goals[goal_name]
                cfg = goal_cfg[goal_name]
                if goal.match(self.player, cfg):
                    logging.debug(f"selector matched a goal {goal.__class__.__name__}")
                    yield goal

import logging

import torch

from deepselector.data_loader import load_data
from deepselector.model import SubGoalSelector
from env.AI.deep_goals import sub_goals_dict, sub_goals
from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal

class DeepAI:
    def __init__(self, player):
        self.player = player
        self.model = None
        self.init_model()

    def init_model(self):
        model = SubGoalSelector()
        model.load_state_dict(torch.load("./model/model_100000.pth"))
        self.model = model

    def update(self):
        sub_goal = self.select(self.player)
        if sub_goal and sub_goal.update(self.player):
            self.player.cur_sub_goal = sub_goal.__class__.__name__
            self.player.cur_goal = ""
            logging.debug(f"new sub_goal {sub_goal.__class__.__name__} selected execute success")
        elif sub_goal:
            logging.debug(f"new sub_goal {sub_goal.__class__.__name__} selected, execute failed")

    def select(self, player) -> BaseSubGoal:
        line = player.env.observe()
        data = load_data(line)[0]
        data = torch.from_numpy(data)
        idx = torch.argmax(self.model(data), dim=0).item()
        idx = 8 if idx == 4 else idx
        return sub_goals_dict[sub_goals[idx]]

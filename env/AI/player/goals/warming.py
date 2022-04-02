from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.collecting_for_materials import CollectingForMaterials
from env.AI.player.goals.sub_goals.make_clothes import MakeClothes
from env.AI.player.goals.sub_goals.wear_clothes import WearClothes


class WarmGoal(BaseGoal):
    def __init__(self):
        super().__init__()
        self.sub_goals = [WearClothes(), MakeClothes(), CollectingForMaterials()]

    def matched(self, player, cfg) -> bool:
        fells_temperature = player.get_fells_temperature()
        if cfg.temperature[0] <= fells_temperature < cfg.temperature[1]:
            return False
        return True

    def update(self, player):
        for sg in self.sub_goals:
            if sg.update(player):
                return True
        return False

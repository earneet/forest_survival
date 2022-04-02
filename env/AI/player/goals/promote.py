from env.AI.player.goals.basegoal import BaseGoal
from env.AI.player.goals.sub_goals.collecting_equip import CollectingEquip
from env.AI.player.goals.sub_goals.collecting_herb import CollectingHerb
from env.AI.player.goals.sub_goals.equip_or_make_equipment import EquipOrMakeEquipment


class PromoteGoal(BaseGoal):
    def __init__(self):
        super().__init__()
        self.sub_goals = [CollectingHerb(), EquipOrMakeEquipment(), CollectingEquip()]

    def match(self, player, cfg) -> bool:
        return True

    def update(self, player):
        for sg in self.sub_goals:
            if sg.update(player):
                return True
        return False

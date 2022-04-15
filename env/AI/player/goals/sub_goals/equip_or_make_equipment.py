
from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
from env.common import PlayerState, SlotType
from env.items.item import Equip


class EquipOrMakeEquipment(BaseSubGoal):
    def __init__(self):
        super(EquipOrMakeEquipment, self).__init__()

    def update(self, player) -> bool:
        if player.equips[SlotType.EQUIP]:   # have equiped one
            return False

        equip_idx = self.find_equipment(player)
        if equip_idx >= 0:                   # equip in the bag
            player.use(equip_idx)
            return True
        if player.state == PlayerState.MAKING:  # making equipment
            return True
        return False

    @staticmethod
    def find_equipment(player) -> int:
        for i, item in enumerate(player.handy_items):
            if isinstance(item[0], Equip):
                return i
        return -1

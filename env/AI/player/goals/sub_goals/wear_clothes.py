
from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
from env.common import SlotType
from env.items.item import Cloth
from env.player.logic.player_common_logic import get_comfortable_temperatures


class WearClothes(BaseSubGoal):
    def __init__(self):
        super(WearClothes, self).__init__()

    def update(self, player) -> bool:
        t_low, t_high = get_comfortable_temperatures()
        fells_temperature = player.get_fells_temperature()
        naked_temperature = player.get_naked_temperature()
        if t_low <= fells_temperature <= t_high:
            return True
        elif naked_temperature > t_high:
            return self.dress(player, t_high - naked_temperature, t_low - naked_temperature)
        elif naked_temperature < t_low:
            return self.dress(player, naked_temperature - t_low, naked_temperature - t_high)
        else:
            player.un_equip(SlotType.CLOTH)
            return True

    def dress(self, player, low, high) -> bool:
        handy_idx = self.find_available(player, low, high)
        if handy_idx >= 0:
            player.use(handy_idx)
            return True
        else:
            box_idx = self.find_available(player, low, high, False)
            if box_idx < 0:
                return False
            if player.in_home():
                player.home2handy(box_idx)
            else:
                player.move_home()
            return True

    @staticmethod
    def find_available(player, low, high, handy=True) -> int:
        items = player.handy_items if handy else player.home_items
        for i, item in enumerate(items):
            if isinstance(item[0], Cloth) and low <= item[0].get_temperature_delta() <= high:
                return i
        return -1

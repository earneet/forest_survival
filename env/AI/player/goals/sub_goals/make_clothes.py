from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
from env.common import PlayerState
from env.items.item import get_recipe_materials
from env.player.logic.player_common_logic import material_enough, get_comfortable_temperatures, find_clothes


class MakeClothes(BaseSubGoal):
    def __init__(self):
        super(MakeClothes, self).__init__()

    def update(self, player) -> bool:
        if player.state == PlayerState.MAKING:
            return True
        low, high = get_comfortable_temperatures()
        naked_temperature = player.get_naked_temperature()
        clothes = find_clothes(low - naked_temperature, high - naked_temperature)   # find the clothe to make
        for cloth in clothes:
            if material_enough(player, cloth):  # can make immediately with enough materials
                player.make(cloth)
                return True

        for cloth in clothes:
            if material_enough(player, cloth, False):   # go home and take the materials
                if player.in_home():
                    self.trans_materials(player, cloth)
                    player.make(cloth)
                else:
                    player.move_home()
                return True
        return False

    @staticmethod
    def trans_materials(player, cloth):
        need_materials = get_recipe_materials(cloth)
        handy_materials = {}
        difference_materials = {}
        for item in player.handy_items:
            material_name = item[0] if isinstance(item[0], str) else item[0].name()
            if material_name not in need_materials:
                continue
            try:
                handy_materials[material_name] += item[1]
            except KeyError:
                handy_materials[material_name] = item[1]

        for material, cnt in need_materials.items():
            if material in handy_materials:
                difference_materials[material] = max(cnt - handy_materials[material], 0)
            else:
                difference_materials[material] = cnt

        for idx, item in enumerate(player.home_items):
            material_name = item[0] if isinstance(item[0], str) else item[0].name()
            if material_name not in difference_materials:
                continue
            else:
                if item[1] >= difference_materials[material_name]:
                    for _ in range(difference_materials[material_name]):
                        player.home2handy(idx)
                    del difference_materials[material_name]
                else:
                    for _ in range(item[1]):
                        player.home2handy(idx)
                    difference_materials[material_name] -= item[1]

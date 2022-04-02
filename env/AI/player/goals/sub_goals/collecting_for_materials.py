from itertools import chain
import numpy as np

from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
from env.items.item import get_recipe_materials
from env.player.logic import get_comfortable_temperatures
from env.player.logic.player_common_logic import find_clothes, diff_materials


class CollectingForMaterials(BaseSubGoal):
    def __init__(self):
        super(CollectingForMaterials, self).__init__()

    def update(self, player) -> bool:
        low, high = get_comfortable_temperatures()
        naked_temperature = player.get_naked_temperature()
        clothes = find_clothes(low - naked_temperature, high - naked_temperature)
        if not clothes:
            return False
        want_cloth = clothes[0]     # ok make this cloth
        materials = get_recipe_materials(want_cloth)    # this cloth need these materials
        diffed_materials = diff_materials(player, materials)
        target = self.search_materials_target(player, diffed_materials)
        if not target:
            return False

        if player.in_attack_range(target):
            player.attack(target)
        else:
            player.move_to(target.position)
        return True

    def search_materials_target(self, player, materials):
        # improve find the most value target, comprehensively drop materials, distance, combat power and other factors
        env = player.env
        pos = player.position
        all_candidates = list(chain(env.animals, env.plants))
        all_candidates.sort(key=lambda x: np.linalg.norm(x.position - pos))
        for c in all_candidates:
            if self.contain_materials(c, materials):
                return c

    @staticmethod
    def contain_materials(game_obj, materials) -> bool:
        drop_cfg = game_obj.cfg.drop or {}
        return bool(drop_cfg.keys() & materials.keys())

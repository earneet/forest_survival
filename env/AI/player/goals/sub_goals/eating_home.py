from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal
from env.items import prop_cfg


class EatingHome(BaseSubGoal):
    """
    Eating the food in the handy bag
    """
    def __init__(self):
        super(EatingHome, self).__init__()

    def update(self, player) -> bool:
        if player.get_food_cnt() <= 0:
            return False
        items = player.get_foods(False)
        use_item_idx = self.find_best_items(items, player)
        if use_item_idx < 0:
            return False
        if player.in_home():
            player.use(use_item_idx)
            return True
        else:
            player.move_home()
            return True

    @staticmethod
    def find_best_items(items, player) -> int:
        if not items:
            return -1
        hp_diff = player.hp_max - player.hp
        # todo in this time , ignore the hunger overflow
        # hunger_diff = player.hunger_max - player.hunger

        max_recover_hp = 0
        hp_item = items[0]
        for item in items:
            item_name = item[1]
            cfg = prop_cfg[item_name]
            if cfg.effect.hp and max_recover_hp < cfg.effect.hp <= hp_diff:
                max_recover_hp = cfg.effect.hp
                hp_item = item
        return hp_item[0]

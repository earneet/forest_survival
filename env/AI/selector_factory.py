from env.AI.selector import Selector, PlayerInnerSelector
from env.common.ai_config import get_ai_config


class SelectorFactory:
    def __init__(self):
        pass

    @staticmethod
    def make_selector(player) -> Selector:
        return PlayerInnerSelector(player, get_ai_config(player.disposition))

    def __call__(self, player) -> Selector:
        return self.make_selector(player)

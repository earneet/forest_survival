from typing import Union

from .ai_instance import AI
from .deep_ai_instance import DeepAI
from .selector import PlayerInnerSelector
from .selector_factory import SelectorFactory


def make_ai_instance(player) -> Union[AI, DeepAI]:
    if player.env.ai == "rule":
        return AI(player, SelectorFactory())
    elif player.env.ai == "deep":
        return DeepAI(player)

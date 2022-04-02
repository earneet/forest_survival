from typing import Optional

from .ai_instance import AI
from .selector import PlayerInnerSelector
from .selector_factory import SelectorFactory


def make_ai_instance(player) -> Optional[AI]:
    return AI(player, SelectorFactory())

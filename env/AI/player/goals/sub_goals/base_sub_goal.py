import abc

import numpy as np


class BaseSubGoal(abc.ABC):
    def __init__(self):
        pass

    def update(self, player) -> bool:
        pass

    def get_around_player(self, player):
        self_pos = player.position
        players = sorted(player.env.players, key=lambda x: np.linalg.norm(self_pos - x.position))
        return list(filter(lambda x: x != player, players))

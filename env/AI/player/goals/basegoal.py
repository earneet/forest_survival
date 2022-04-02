import abc

class BaseGoal(abc.ABC):
    def __init__(self):
        pass

    def match(self, player, cfg) -> bool:
        pass

    def update(self, player) -> bool:
        pass

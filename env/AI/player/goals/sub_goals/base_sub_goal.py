import abc


class BaseSubGoal(abc.ABC):
    def __init__(self):
        pass

    def update(self, player) -> bool:
        pass

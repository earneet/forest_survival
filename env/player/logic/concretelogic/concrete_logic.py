import abc


class PlayerConcreteLogic(abc.ABC):
    def __init__(self, player, parent_logic):
        self.player = player
        self.parent_logic = parent_logic

    def can_enter_state(self, *_) -> bool:
        assert self
        return True

    def on_enter_state(self, *_):
        pass

    def on_leave_state(self, *_):
        pass

    def update(self):
        pass



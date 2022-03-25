from env.player.logic.concretelogic.concrete_logic import PlayerConcreteLogic


class PlayerRestingLogic(PlayerConcreteLogic):
    def __init__(self, player, logic):
        super(PlayerRestingLogic, self).__init__(player, logic)
        self.parent_logic = logic

    def update(self):
        pass

    def on_enter_state(self, *args):
        pass

    def on_leave_state(self, *args):
        pass


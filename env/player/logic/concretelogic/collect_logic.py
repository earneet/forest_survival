from env.common import PlayerState
from env.player.logic.concretelogic.concrete_logic import PlayerConcreteLogic


class PlayerCollectLogic(PlayerConcreteLogic):
    def __init__(self, player, logic):
        super(PlayerCollectLogic, self).__init__(player, logic)
        self.target = None

    def on_enter_state(self, target):
        self.target = target
        self.parent_logic.cur_logic = self
        self.player.interact_target = target
        self.player.state = PlayerState.COLLECTING
        self.player.sub_state = None
        self.target.collect(self.player)

    def on_leave_state(self):
        self.player.state = PlayerState.IDLE
        if self.target and not self.target.is_dead():
            self.target.stop_collect(self.player)
        self.target = None

    def update(self):
        pass

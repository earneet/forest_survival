from env.common import PlayerState
from env.items import make_cloth, make_equip
from env.player.logic.concretelogic.concrete_logic import PlayerConcreteLogic


class PlayerMakeLogic(PlayerConcreteLogic):
    def __init__(self, player, logic):
        super(PlayerMakeLogic, self).__init__(player, logic)
        self.making_cfg = None
        self.success_frame = None

    def update(self):
        frame = self.player.frames
        if frame < self.success_frame:
            return
        self._make(self.making_cfg.name, self.making_cfg)
        self.on_leave_state()
        return

    def on_enter_state(self, *args):
        self.player.make_frame = self.player.frames
        self.making_cfg = args[0]
        self.success_frame = int(
            self.making_cfg.recipe.time_consuming * self.player.env.HOUR_FRAMES) + self.player.frames
        self.player.state = PlayerState.MAKING
        self.parent_logic.cur_logic = self

    def on_leave_state(self, *_):
        self.player.state = PlayerState.IDLE
        self.player.sub_state = None
        target = self.player.interact_target
        if target and not target.is_dead():
            target.stop_collect(self.player)
        self.making_cfg = None
        self.parent_logic.cur_logic = None
        self.player.make_frame = 0

    def _make(self, item, cfg) -> bool:
        production = None
        if item.endswith("_clothes"):
            production = make_cloth(item)
        elif item.endswith("_equip"):
            production = make_equip(item)
        if production:
            self.parent_logic.remove_cost(cfg.recipe.materials)
            self.parent_logic.put_handy(production)
            return True
        return False

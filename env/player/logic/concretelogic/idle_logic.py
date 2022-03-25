from env.player.logic.concretelogic.concrete_logic import PlayerConcreteLogic


class PlayerIdleLogic(PlayerConcreteLogic):
    def __init__(self, player, logic):
        super(PlayerIdleLogic, self).__init__(player, logic)

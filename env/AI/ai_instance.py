

class AI:
    def __init__(self, player, selector_factory=None):
        self.player = player
        self.selector_factory = selector_factory

    def update(self):
        selector = self.selector_factory.make_selector(self.player)
        for goal in selector:
            if goal.update(self.player):
                self.player.cur_goal = goal.__class__.__name__
                return True
        else:
            self.player.cur_goal = ""

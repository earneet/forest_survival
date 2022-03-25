

class AI:
    def __init__(self):
        self.player = None
        self.goal = None
        self.selector = None

    def update(self):
        new_goal = self.selector.select(self.player)
        if new_goal != self.goal:
            self.goal = new_goal

        self.goal.update()

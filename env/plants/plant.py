import abc

from env.engine.gameitem import GameItem


class Plant(GameItem, abc.ABC):
    def __init__(self):
        super().__init__()
        self.collectors = {}

    def collect(self, player, frame):
        self.collectors[player.id] = frame

    def stop_collect(self, player):
        del self.collectors[player.id]

    def update(self):
        if not self.collectors:
            return

        for p, f in self.collectors.items():
            pass

    def on_collected(self, player):
        pass


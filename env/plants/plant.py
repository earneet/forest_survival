import abc

from env.engine.gameitem import GameItem


class Plant(GameItem, abc.ABC):
    def __init__(self, cfg):
        super().__init__()
        self.collectors = {}
        self.cfg = cfg
        self.hp = 1     # all plants has a default hp value 1, when it be collected, change to 0
        self.position = [0, 0]
        self._species = cfg.species

    @property
    def species(self) -> str:
        return self._species

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


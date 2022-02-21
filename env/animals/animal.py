import abc

from env.engine.gameitem import GameItem


class Animal(GameItem, abc.ABC):
    def __init__(self):
        super().__init__()
        self.hp = 1
        self.move_speed = 1
        self.resource = {}
        self.ai_instance = None
        self._species = 'sheep'

    def update(self):
        if self.ai_instance:
            self.ai_instance.update()

    def species(self):
        assert self is not None
        return ""

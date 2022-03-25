import pygame as pg

from env.common import Terrain
from env.engine.utils import load_image


class EMapCell(pg.sprite.Sprite):
    containers = None
    terrain2images = {}

    def __init__(self, game_obj, engine):
        super(EMapCell, self).__init__(self.containers)
        self.game_obj = game_obj
        self.engine = engine

        if not self.terrain2images:
            self.terrain2images = {
                Terrain.FOREST: load_image("forest.png"),
                Terrain.LAWN: load_image("lawn.png"),
                Terrain.RIVER: load_image("river.png"),
                Terrain.HOUSE: load_image("house.png"),
                Terrain.SELF_HOUSE: load_image("house2.png")
            }
        x = self.game_obj.x * 20
        y = self.game_obj.y * 20
        self.image = self.terrain2images[self.game_obj.type]
        self.rect = self.image.get_rect()
        self.rect.move_ip(x, y)

    def update(self):
        pass

    def check_click(self, pos, button):
        if not self.rect.collidepoint(pos):
            return False
        if button == pg.BUTTON_RIGHT:
            self.engine.move_to(pos)
            return True
        return False

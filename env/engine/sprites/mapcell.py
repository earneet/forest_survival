import pygame as pg

from map import Terrain


class EMapCell(pg.sprite.Sprite):
    terrain2images = {}
    containers = None

    def __init__(self, game_obj):
        super().__init__(self.containers)
        self.game_obj = game_obj

        from engine.utils import load_image
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

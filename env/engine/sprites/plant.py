import pygame as pg

from env.plants import plant_cfg
from env.engine.utils import load_image


class EPlant(pg.sprite.Sprite):
    plants2image = {}
    containers = None

    def __init__(self, game_obj):
        super(EPlant, self).__init__(self.containers)
        self.game_obj = game_obj
        if not self.plants2image:
            for name in plant_cfg:
                self.plants2image[name] = load_image(name+".png", -1)
        self.image = self.plants2image[self.game_obj.species]
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.game_obj.position[0], self.game_obj.position[1]

    def update(self):
        self.rect.centerx, self.rect.centery = self.game_obj.position[0], self.game_obj.position[1]

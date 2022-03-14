import logging

import pygame as pg

from plants import plant_cfg


class EPlant(pg.sprite.Sprite):
    plants2image = {}
    containers = None

    def __init__(self, game_obj):
        super(EPlant, self).__init__(self.containers)
        self.game_obj = game_obj
        from engine.engine import load_image
        if not self.plants2image:
            for name in plant_cfg:
                self.plants2image[name] = load_image(name+".png", -1)
        self.image = self.plants2image[self.game_obj.species]
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.game_obj.position[0], self.game_obj.position[1]

    def update(self):
        self.rect.centerx, self.rect.centery = self.game_obj.position[0], self.game_obj.position[1]

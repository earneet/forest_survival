
import pygame as pg


class EAnimal(pg.sprite.Sprite):
    def __init__(self, game_obj):
        super(EAnimal, self).__init__()
        self.game_obj = game_obj

    def update(self):
        pass

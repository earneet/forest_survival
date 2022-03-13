import pygame as pg


class EMapCell(pg.sprite.Sprite):
    def __init__(self, game_obj):
        super().__init__()
        self.game_obj = game_obj

    def update(self):
        pass

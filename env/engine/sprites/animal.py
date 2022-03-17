import pygame as pg
from env.animals import animal_cfg
from env.engine.utils import load_image


class EAnimal(pg.sprite.Sprite):
    animal2image = {}
    containers = None

    def __init__(self, game_obj):
        super(EAnimal, self).__init__(self.containers)
        self.game_obj = game_obj
        if not self.animal2image:
            for name in animal_cfg:
                self.animal2image[name] = load_image(name+".png", -1)
        self.image = self.animal2image[self.game_obj.species]
        self.rect = self.image.get_rect()
        # self.rect.move_ip(self.game_obj.position[0], self.game_obj.position[1])
        self.rect.centerx, self.rect.centery = self.game_obj.position[0], self.game_obj.position[1]

    def update(self):
        self.rect.centerx, self.rect.centery = self.game_obj.position[0], self.game_obj.position[1]

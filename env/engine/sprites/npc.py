import pygame as pg


class ENpc(pg.sprite.Sprite):
    images = []
    containers = None

    def __init__(self, game_obj):
        super().__init__(self.containers)
        self.game_obj = game_obj
        if not self.images:
            from engine.utils import load_image
            self.images.append(load_image("player.png"))
            self.images.append(load_image("npc.png"))
        self.image = self.images[0] if self.game_obj == self.game_obj.env.players[0] else self.images[1]
        self.rect = self.image.get_rect()
        self.update_pos()

    def update(self):
        self.update_pos()

    def update_pos(self):
        width, height = self.rect.width, self.rect.height
        self.rect.centerx = self.game_obj.position[0]
        self.rect.centery = self.game_obj.position[1]

import pygame as pg

from env.player import PlayerState


class EOpponentInfo(pg.sprite.Sprite):
    containers = None

    def __init__(self, game_obj):
        super(EOpponentInfo, self).__init__(self.containers)
        self.game_obj = game_obj
        self.image = pg.Surface((200, 30))
        self.rect = self.image.get_rect().move(410, 250)
        self.font = pg.font.Font(None, 20)
        self.text_color = pg.color.Color("white")
        self.gap = 1

    def update(self):
        self.image.fill("black")
        if self.game_obj.state != PlayerState.BATTLING:
            return

        target = self.game_obj.interact_target
        target_name = target.get_name()
        target_hp = target.hp

        name_image = self.font.render(f"o_name: {target_name}", True, self.text_color)
        hp_image = self.font.render(f"hp: {target_hp}", True, self.text_color)

        total_height = 1
        self.image.blit(name_image, (0, total_height))
        total_height += name_image.get_height() + self.gap
        self.image.blit(hp_image, (0, total_height))
        total_height += name_image.get_height() + self.gap


import pygame as pg


class EPlayerInfo(pg.sprite.Sprite):
    containers = None

    def __init__(self, game_obj):
        super(EPlayerInfo, self).__init__(self.containers)
        self.game_obj = game_obj
        self.font = pg.font.Font(None, 20)
        self.font.set_italic(True)
        self.color = pg.color.Color("white")
        self.image = pg.surface.Surface((100, 300))
        self.rect = self.image.get_rect().move(400, 0)
        self.update()

    def update(self):
        state_msg = f"state:  {self.game_obj.state.name}"
        sub_state_msg = f"sstate:  {self.game_obj.sub_state.name if self.game_obj.sub_state else ''}"
        hp_msg = f"hp:   {self.game_obj.hp} / {self.game_obj.hp_max}"
        dir_msg = f"dir:   {self.game_obj.direction}"
        speed_msg = f"speed:   {self.game_obj.speed}"
        hunger_msg = f"hunger:   {self.game_obj.hunger}"
        energy_msg = f"energy:   {self.game_obj.energy}"

        state_img = self.font.render(state_msg, True, self.color)
        sub_state_img = self.font.render(sub_state_msg, True, self.color)
        hp_img = self.font.render(hp_msg, True, self.color)
        dir_img = self.font.render(dir_msg, True, self.color)
        speed_img = self.font.render(speed_msg, True, self.color)
        hunger_img = self.font.render(hunger_msg, True, self.color)
        energy_img = self.font.render(energy_msg, True, self.color)

        self.image.fill(pg.color.Color("black"))
        total_height = 0
        self.image.blit(state_img, (0, total_height))
        total_height += state_img.get_height() + 1
        self.image.blit(sub_state_img, (0, total_height))
        total_height += sub_state_img.get_height() + 1
        self.image.blit(hp_img, (0, total_height))
        total_height += hp_img.get_height() + 1
        self.image.blit(dir_img, (0, total_height))
        total_height += dir_img.get_height() + 1
        self.image.blit(speed_img, (0, total_height))
        total_height += speed_img.get_height() + 1
        self.image.blit(hunger_img, (0, total_height))
        total_height += hunger_img.get_height()
        self.image.blit(energy_img, (0, total_height))
        total_height += hunger_img.get_height()


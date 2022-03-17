import logging

import pygame as pg

from engine.utils import load_image
from event import UnEquip
from items import equip_cfg, clothes_cfg


class EEquipBag(pg.sprite.Sprite):
    containers = None
    item2images = {}
    empty_image = pg.Surface((20, 20))
    empty_image.fill(pg.color.Color("black"))

    def __init__(self, game_obj):
        super(EEquipBag, self).__init__(self.containers)
        self.game_obj = game_obj
        if not self.item2images:
            for cfgs in [equip_cfg, clothes_cfg]:
                for name in cfgs:
                    self.item2images[name] = load_image(name + ".png")
        self.font = pg.font.Font(None, 20)
        self.text_color = pg.color.Color("white")
        self.gap = 1
        self.image = pg.Surface((50, 45))
        self.rect = self.image.get_rect().move(0, 450)

    def update(self):
        total_width = 1
        self.image.fill("black")
        for slot in self.game_obj.equips:
            if slot is None:
                image = self.empty_image
                wear_image = image
            else:
                image = self.item2images[slot.name()]
                wear_image = self.font.render(str(slot.wear), True, self.text_color)
            self.image.blit(image, (total_width, 0))
            self.image.blit(wear_image, (total_width, 21))
            total_width += image.get_width() + self.gap

    def check_click(self, pos, button):
        x, y = pos
        if not self.rect.collidepoint(x, y):
            return False
        idx = (x - self.rect.left) // (20 + self.gap)
        if idx > 2:
            return False

        if button == pg.BUTTON_RIGHT and idx < len(self.item2images):
            self.game_obj.receive_event(UnEquip(idx))
            logging.info(f"UnEquip Occured {idx}")
            return True
        return False

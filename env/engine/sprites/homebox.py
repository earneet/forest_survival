import logging

import pygame as pg

from env.engine.utils import load_image
from common.event.event import Exchange
from env.items import equip_cfg, clothes_cfg, prop_cfg


class EHomeBox(pg.sprite.Sprite):
    item2images = {}
    black = pg.Surface((20, 20))
    black.fill(pg.color.Color("black"))
    containers = None

    def __init__(self, game_obj):
        super(EHomeBox, self).__init__(self.containers)
        self.game_obj = game_obj
        self.font = pg.font.Font(None, 20)
        self.font.set_italic(True)
        self.text_color = pg.color.Color("white")
        self.gap = 1
        self.cell_width = 20 + self.gap
        if not self.item2images:
            for cfgs in [equip_cfg, clothes_cfg, prop_cfg]:
                for name, cfg in cfgs.items():
                    try:
                        self.item2images[name] = load_image(name + ".png")
                    except FileNotFoundError:
                        logging.error(f"Can't load image {name + '.png'}")

        self.image = pg.surface.Surface((120, 45))
        self.rect = self.image.get_rect().move(410, 350)
        self.update()

    def update(self):
        self.image.fill(pg.color.Color("black"))
        handy_items = self.game_obj.home_items
        total_width = 1
        for item in handy_items:
            if item[0] is None:
                image = self.black
                cnt_image = image
            elif isinstance(item[0], str):
                image = self.item2images[item[0]]
                cnt_image = self.font.render(f"{item[1]}", True, self.text_color)
            else:
                image = self.item2images[item[0].name()]
                cnt_image = self.font.render(f"{item[1]}", True, self.text_color)
            self.image.blit(image, (total_width, 0))
            self.image.blit(cnt_image, (total_width, 22))
            total_width += image.get_width() + self.gap

    def check_click(self, pos, _):
        x, y = pos
        if not self.rect.collidepoint(x, y):
            return False

        idx = (x - self.rect.left) // self.cell_width
        if 0 <= idx < len(self.game_obj.home_items):
            self.game_obj.receive_event(Exchange(idx, True))

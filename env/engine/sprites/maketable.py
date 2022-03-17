from collections import OrderedDict

import pygame as pg

from env.engine.utils import load_image
from common.event.event import MakeItem
from env.items import equip_cfg, clothes_cfg


class EMakeTable(pg.sprite.Sprite):
    item2images = OrderedDict()
    idx2name = []
    containers = None

    def __init__(self, game_obj):
        super(EMakeTable, self).__init__(self.containers)
        if not self.item2images:
            for cfgs in [equip_cfg, clothes_cfg]:
                for name in cfgs:
                    self.item2images[name] = load_image(name + ".png")
                    self.idx2name.append(name)

        self.game_obj = game_obj
        self.gas = 1
        self.image = pg.Surface((100, 30))
        self.rect = self.image.get_rect().move(410, 410)
        self.update()

    def update(self):
        total_width = 1
        for name, img in self.item2images.items():
            self.image.blit(img, (total_width, 0))
            total_width += img.get_width() + self.gas

    def check_click(self, pos, button):
        x, y = pos
        if not self.rect.collidepoint(x, y):
            return False
        idx = (x - self.rect.left) // (20 + self.gas)
        if button == pg.BUTTON_LEFT and idx < len(self.idx2name):
            self.game_obj.receive_event(MakeItem(self.idx2name[idx]))
            return True
        return False

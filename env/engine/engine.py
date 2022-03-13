from . import GameItem
import pygame as pg
import os
import logging
from .sprites.animal import EAnimal
from .sprites.mapcell import EMapCell
from .sprites.npc import ENpc
from .sprites.plant import EPlant

root_dir = os.path.dirname(__file__)
data_dir = os.path.join(root_dir, "res")


def load_images(name, colorkey=None, scale=1):
    full_name = os.path.join(data_dir, name)
    image = pg.image.load(full_name)
    size = image.get_size()
    size = (size.width * scale, size.height * scale)
    image = pg.transform.scale(image, size)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    pass


class Engine:
    def __init__(self, env):
        self._env = env
        self.game_items = {}
        self.mapcells_g = None
        self.plants_g = None
        self.animals_g = None
        self.players_g = None
        self.all_g = None

    def reset(self):
        pg.init()
        pg.display.set_mode((540, 360), pg.SCALED)
        self.mapcells_g = pg.sprite.Group()
        self.players_g = pg.sprite.Group()
        self.animals_g = pg.sprite.Group()
        self.plants_g = pg.sprite.Group()
        self.all_g = pg.sprite.RenderUpdates()

        ENpc.containers = self.players_g, self.all_g
        EAnimal.containers = self.animals_g, self.all_g
        EPlant.containers = self.plants_g, self.all_g
        EMapCell.containers = self.mapcells_g, self.all_g

        # prepare map cell sprite
        map = self._env.map
        for cell in map.cells:
            ecell = EMapCell(cell)

    def render(self):
        logging.debug("Render")
        self.all_g.update()
        for e in pg.event.get():
            pass

    def quit(self):
        pg.quit()
        self.mapcells_g = None
        self.players_g = None
        self.animals_g = None
        self.plants_g = None
        self.all_g = None

    def spawn(self, game_item: GameItem, parent: GameItem = None):
        assert game_item is not None, "game item can't be None Value"
        if game_item.id in self.game_items:
            return

        self.game_items[game_item.id] = game_item
        if parent is not None:
            parent.add_child(game_item)

    def update(self):
        # put draw canvas code here
        pass

    @staticmethod
    def get_instance():
        return _engine


_engine = Engine()


def get_engine():
    return _engine



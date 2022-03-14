import sys

import pygame as pg
import os
import logging

from event import MoveUp, MoveRight, MoveDown, MoveLeft, StopMove
from .sprites.animal import EAnimal
from .sprites.mapcell import EMapCell
from .sprites.npc import ENpc
from .sprites.plant import EPlant

root_dir = os.path.dirname(__file__)
data_dir = os.path.join(root_dir, "res")


def load_image(name, colorkey=None, scale=1):
    full_name = os.path.join(data_dir, name)
    image = pg.image.load(full_name)
    size = image.get_size()
    size = (int(size[0] * scale), int(size[1] * scale))
    image = pg.transform.scale(image, size)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((2, 2))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image


def load_sound(name):
    if not pg.mixer:
        return None
    file = os.path.join(data_dir, name)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        logging.warning(f"Warning, unable to load, {file}")
    return None


class Engine:
    def __init__(self):
        self.game_items = {}
        self.mapcells_g = None
        self.plants_g = None
        self.animals_g = None
        self.players_g = None
        self.all_g = None
        self.screen = None
        self._env = None
        self.players = []
        self.animals = []
        self.plants = []
        self.cells = []
        self.clock = pg.time.Clock()
        self.fps = 10
        self.background = None

    def set_env(self, env):
        assert env is not None, "env must a valid environment"
        self._env = env

    def reset(self):
        pg.init()
        winstyle = 0
        SCREENRECT = pg.Rect(0, 0, 640, 480)
        bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
        self.screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
        #self.screen = pg.display.set_mode((640, 480))
        self.background = pg.surface.Surface(SCREENRECT.size)
        pg.display.set_caption("forest_survival")
        self.mapcells_g = pg.sprite.Group()
        self.players_g = pg.sprite.Group()
        self.animals_g = pg.sprite.Group()
        self.plants_g = pg.sprite.Group()
        self.all_g = pg.sprite.RenderUpdates()

        EMapCell.containers = self.all_g
        ENpc.containers = self.players_g, self.all_g
        EAnimal.containers = self.animals_g, self.all_g
        EPlant.containers = self.plants_g, self.all_g
        EMapCell.containers = self.mapcells_g, self.all_g

        # prepare map cell sprite
        map = self._env.map
        for cell in map.cells:
            self.cells.append(EMapCell(cell))

    def render(self):
        self.all_g.draw(self.screen)
        pg.display.update()
        return

        for cell in self.cells:
            self.background.blit(cell.image, cell.rect)

        for plant in self.plants:
            self.background.blit(plant.image, plant.rect)

        for animal in self.animals:
            self.background.blit(animal.image, animal.rect)

        for player in self.players:
            self.background.blit(player.image, player.rect)

        self.screen.blit(self.background, self.background.get_rect())
        pg.display.flip()

    def process_event(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                sys.exit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                self._process_mouse_click(e)
            elif e.type == pg.KEYDOWN:
                self._process_key_down(e)
            elif e.type == pg.KEYUP:
                self._process_key_up(e)

    def _process_key_down(self, event):
        key = event.key
        if key == pg.K_UP:
            self._env.players[0].receive_event(MoveUp())
        if key == pg.K_RIGHT:
            self._env.players[0].receive_event(MoveRight())
        elif key == pg.K_DOWN:
            self._env.players[0].receive_event(MoveDown())
        elif key == pg.K_LEFT:
            self._env.players[0].receive_event(MoveLeft())

    def _process_key_up(self, event):
        key = event.key
        self._env.players[0].receive_event(StopMove())

    def _process_mouse_click(self, event):
        x, y = event.pos
        logging.info(f"mouse clicked at ({x} {y})")

    def quit(self):
        self.mapcells_g = None
        self.players_g = None
        self.animals_g = None
        self.plants_g = None
        self.all_g = None
        pg.quit()

    def update(self):
        self._do_diff()
        self.all_g.clear(self.screen, self.background)
        self.all_g.update()
        self.process_event()
        self.render()
        self.clock.tick(10)

    @staticmethod
    def get_instance():
        return _engine

    def _do_diff(self):
        new_players, dumped_players = self._find_diff_players()
        new_plants, dumped_plants = self._find_diff_plants()
        new_animals, dumped_animals = self._find_diff_animals()

        players = [p for p in self.players if p not in dumped_players]
        for new_player in new_players:
            players.append(ENpc(new_player))
        self.players = players

        plants = [p for p in self.plants if p not in dumped_plants]
        for new_plant in new_plants:
            plants.append(EPlant(new_plant))
        self.plants = plants

        animals = [a for a in self.animals if a not in dumped_animals]
        for new_animal in new_animals:
            animals.append(EAnimal(new_animal))
        self.animals = animals

    def _find_diff_players(self):
        cur = self._env.players
        pre = self.players
        return self._find_diff(cur, pre)

    def _find_diff_animals(self):
        cur = self._env.animals
        pre = self.animals
        return self._find_diff(cur, pre)

    def _find_diff_plants(self):
        cur = self._env.plants
        pre = self.plants
        return self._find_diff(cur, pre)

    @staticmethod
    def _find_diff(cur, pre):
        cur_set = set(cur)
        pre_set = set([p.game_obj for p in pre])
        dumped = [p for p in pre if p.game_obj not in cur_set]
        return cur_set.difference(pre_set), dumped


_engine = Engine()


def get_engine():
    return _engine



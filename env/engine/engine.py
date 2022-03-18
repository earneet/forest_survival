import sys

import pygame as pg

from env.common.event.event import *
from .sprites.animal import EAnimal
from .sprites.equipbag import EEquipBag
from .sprites.homebox import EHomeBox
from .sprites.maketable import EMakeTable
from .sprites.handy import EHandy
from .sprites.mapcell import EMapCell
from .sprites.npc import ENpc
from .sprites.opponentinfo import EOpponentInfo
from .sprites.plant import EPlant
from .sprites.playerinfo import EPlayerInfo

move_buttons = {pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT, pg.K_w, pg.K_d, pg.K_s, pg.K_a}


class Engine:
    def __init__(self):
        self.game_items = {}
        self.mapcells_g = None
        self.plants_g = None
        self.animals_g = None
        self.players_g = None
        self.ui_g = None
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
        screenrect = pg.Rect(0, 0, 640, 500)
        bestdepth = pg.display.mode_ok(screenrect.size, winstyle, 32)
        self.screen = pg.display.set_mode(screenrect.size, winstyle, bestdepth)
        self.background = pg.surface.Surface(screenrect.size)
        pg.display.set_caption("forest_survival")
        self.mapcells_g = pg.sprite.Group()
        self.animals_g = pg.sprite.Group()
        self.plants_g = pg.sprite.Group()
        self.players_g = pg.sprite.Group()
        self.ui_g = pg.sprite.Group()
        self.all_g = pg.sprite.RenderUpdates()

        EMapCell.containers = self.all_g
        EAnimal.containers = self.animals_g, self.all_g
        EPlant.containers = self.plants_g, self.all_g
        EMapCell.containers = self.mapcells_g, self.all_g
        ENpc.containers = self.players_g, self.all_g
        EPlayerInfo.containers = self.all_g
        EOpponentInfo.containers = self.all_g
        EHandy.containers = self.ui_g, self.all_g
        EMakeTable.containers = self.ui_g, self.all_g
        EEquipBag.containers = self.ui_g, self.all_g
        EHomeBox.containers = self.ui_g, self.all_g

        # prepare map cell sprite
        for cell in self._env.map.cells:
            self.cells.append(EMapCell(cell))
        EPlayerInfo(self._env.players[0])
        EHandy(self._env.players[0])
        EMakeTable(self._env.players[0])
        EEquipBag(self._env.players[0])
        EOpponentInfo(self._env.players[0])
        EHomeBox(self._env.players[0])

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

    def render(self):
        self.all_g.draw(self.screen)
        pg.display.update()

    def process_event(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                sys.exit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                self._process_mouse_click(e, e.button)
            elif e.type == pg.KEYDOWN:
                self._process_key_down(e)
            elif e.type == pg.KEYUP:
                self._process_key_up(e)

    def _process_key_down(self, event):
        key = event.key
        if key in move_buttons:  # move
            self._process_key_for_move(event)
        elif key == pg.K_c:  # collect
            self._process_key_for_collect(event)
        elif key == pg.K_r:  # rest
            self._process_key_for_rest()
        elif key == pg.K_t:
            self._add_test_item()
        elif key == pg.K_b:
            self._env.players[0].receive_event(Attack())

    def _process_key_for_rest(self):
        self._env.players[0].receive_event(Resting())

    def _process_key_for_collect(self, _):
        self._env.players[0].receive_event(Collecting())

    def _process_key_for_move(self, event):
        key = event.key
        if key == pg.K_UP or key == pg.K_w:
            self._env.players[0].receive_event(MoveUp())
        if key == pg.K_RIGHT or key == pg.K_d:
            self._env.players[0].receive_event(MoveRight())
        elif key == pg.K_DOWN or key == pg.K_s:
            self._env.players[0].receive_event(MoveDown())
        elif key == pg.K_LEFT or key == pg.K_a:
            self._env.players[0].receive_event(MoveLeft())

    def _process_key_up(self, event):
        if event.key not in move_buttons:
            return
        pressed_keys = pg.key.get_pressed()
        for k in move_buttons:
            if pressed_keys[k]:
                return
        self._env.players[0].receive_event(StopMove())

    def _process_mouse_click(self, event, button):
        for sprite in self.ui_g:
            sprite.check_click(event.pos, button)

    def _do_diff(self):
        new_plants, dumped_plants = self._find_diff_plants()
        new_animals, dumped_animals = self._find_diff_animals()
        new_players, dumped_players = self._find_diff_players()

        plants = [p for p in self.plants if p not in dumped_plants]
        for new_plant in new_plants:
            plants.append(EPlant(new_plant))
        self.plants = plants
        for dumped_plant in dumped_plants:
            self.plants_g.remove(dumped_plant)
            self.all_g.remove(dumped_plant)

        animals = [a for a in self.animals if a not in dumped_animals]
        for new_animal in new_animals:
            animals.append(EAnimal(new_animal))
        self.animals = animals
        for dumped_animal in dumped_animals:
            self.animals_g.remove(dumped_animal)
            self.all_g.remove(dumped_animal)

        players = [p for p in self.players if p not in dumped_players]
        for new_player in new_players:
            players.append(ENpc(new_player))
        self.players = players
        for dumped_player in dumped_players:
            self.players_g.remove(dumped_player)
            self.all_g.remove(dumped_player)

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

    def _add_test_item(self):
        self._env.players[0].pickup({
            "wool": 99,
            "cotton": 99,
        })

        self._env.players[0].pickup({
            "wool": 99,
            "cotton": 99,
        }, False)


_engine = Engine()


def get_engine():
    return _engine

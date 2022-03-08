import json
import logging
import os
from queue import Queue
from typing import Dict, Callable

import numpy as np

from animals import new_animal
from map.terrain import string2terrains
from player import Player
from timer import FixedPeriodTimer


class EnvLogic:
    EVENT_SECOND_ELAPSE = "second_elapse"

    def __init__(self, env, frame_rate=10):
        self._env = env
        self._events: Queue = Queue()
        self._events_handlers: Dict[str, Callable] = {}
        self.FRAME_RATE = frame_rate
        self.HOUR_FRAMES = self.FRAME_RATE * env.HOUR_SECOND_RATIO
        self.DAY_FRAMES = self.HOUR_FRAMES * env.DAY_HOUR_RATIO
        self.MONTH_FRAMES = self.DAY_FRAMES * env.MONTH_DAY_RATIO
        self.SEASON_FRAMES = self.MONTH_FRAMES * env.SEASON_MONTH_RATIO
        self.YEAR_FRAMES = self.SEASON_FRAMES * env.YEAR_SEASON_RATIO

    def reset(self):
        timer = self._env.timer
        timer.reset()
        self._reset_map()
        self._init_event_handlers()
        self._add_default_timers()
        self._refresh_init()

    def _reset_map(self):
        env_map = self._env.map
        root_dir = os.path.dirname(os.path.abspath("."))
        cfg_path = os.path.join(root_dir, "gamecfg", "map.json")
        with open(cfg_path) as f:
            cfg = json.load(f)
        env_map.reset(cfg)

    def _init_event_handlers(self):
        self._events_handlers[EnvLogic.EVENT_SECOND_ELAPSE] = self.on_second_elapse

    def update(self):
        # first update timer
        frames = self._env.frames + 1
        self._env.frames += 1
        for player in self._env.players:
            player.update(frames)

        for animal in self._env.animals:
            animal.update(frames)

        self._update_timer(frames)

    def _update_timer(self, frames):
        events = self._env.timer.tick()
        if events:
            for event in events:
                self._events.put(event)

        if frames % self.FRAME_RATE == 0:
            self.on_second_elapse(frames // self.FRAME_RATE)

        day, day_residual, day_change = frames//self.DAY_FRAMES, frames % self.DAY_FRAMES, frames % self.DAY_FRAMES == 0
        if day_change:
            month, month_change = day // 30, day % 30 == 0
            if month_change:
                logging.info(" a new month begin ... ")
                season, season_change = month // 3, month % 3 == 0
                if season_change:
                    self.on_season_change(season)
            self.on_new_day(day)
        elif day_residual == int(self.DAY_FRAMES * 0.25):
            self.on_sun_raise(day)
        elif day_residual == int(self.DAY_FRAMES * 0.5):
            self.on_noon(day)
        elif day_residual == int(self.DAY_FRAMES * 0.75):
            self.on_sun_sink(day)

    def _add_default_timers(self):
        timers = []

        timer = self._env.timer
        timer.add_timer(FixedPeriodTimer(1.0, EnvLogic.EVENT_SECOND_ELAPSE))

    def _refresh_init(self):
        self._refresh_init_players()
        self._refresh_init_animals()
        self._refresh_init_plants()

    def _refresh_init_players(self):
        map = self._env.map
        self._env.players = []
        cells = map.select_cells(5)
        for cell in cells:
            y = cell.y
            x = cell.x
            player = Player(self._env)
            player.position = ((x + 0.5) * map.cell_size, (y + 0.5) * map.cell_size)
            self._env.players.append(player)
            cell.player_move_in(player)

    def _refresh_init_animals(self):
        self._env.animals = []
        self._refresh_animals()

    def _refresh_animals(self):
        from animals import animal_cfg
        residuals = {}
        for species, cfg in animal_cfg.items():
            residuals[species] = 0

        for animal in self._env.animals:
            if animal.hp > 0:
                residuals[animal.species] += 1

        for species, cfg in animal_cfg.items():
            need_cnt = cfg.init_count - residuals[species]
            cells = self._env.map.select_cells(string2terrains(cfg.terrains), size=need_cnt)
            self._refresh_animals_species(species, cfg, cells)

    def _refresh_init_plants(self):
        self._env.plants = []
        from plants import plant_cfg
        residuals = {}
        for species, cfg in plant_cfg.items():
            residuals[species] = 0

        for plant in self._env.plants:
            residuals[plant.species] += 1

        for species, cfg in plant_cfg.items():
            need_cnt = cfg.init_count - residuals[species]
            cells = self._env.map.select_cells(string2terrains(cfg.terrains), size=need_cnt)
            self._refresh_plants_species(species, cfg, cells)

    def _refresh_animals_species(self, species, cfg, cells):
        for cell in cells:
            sp = new_animal(species, cfg)
            pos_x, pos_y = self._env.map.get_cell_center(cell)
            sp.position = np.array([pos_x, pos_y])
            self._env.animals.append(sp)

    def _refresh_plants_species(self, species, cfg, cells):
        for cell in cells:
            sp = new_plant(species, cfg)
            pos_x, pos_y = self._env.map.get_cell_center(cell)
            sp.position = np.array([pos_x, pos_y])
            self._env.animals.append(sp)



    def on_new_day(self, new_day):
        logging.info(" a new day begin ... middle night")
        for player in self._env.players:
            player.on_new_day()
        # refresh day reset

    def on_sun_raise(self, day):
        logging.info(f"day event sun raise ... day {day}")

    def on_noon(self, day):
        logging.info(f"day event the noon ... day {day}")

    def on_sun_sink(self, day):
        logging.info(f"day event the run sink ... day {day}")

    def on_second_elapse(self, event):
        assert self is not None
        logging.debug(f"second elapse ... {event}")

    def on_season_change(self, new_season):
        assert self is not None
        logging.info(" season change ... ")
        logging.info(f" a new season begin ... season {new_season}")


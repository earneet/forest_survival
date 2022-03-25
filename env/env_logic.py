import logging
from queue import Queue

import numpy as np

from env.animals import new_animal
from env.common.terrain import string2terrains
from env.player import make_player
from env.map.map_config import map_cfg


class EnvLogic:
    EVENT_SECOND_ELAPSE = "second_elapse"

    def __init__(self, env, frame_rate=10):
        self._env = env
        self._events: Queue = Queue()
        self.FRAME_RATE = frame_rate
        self.HOUR_FRAMES = self.FRAME_RATE * env.HOUR_SECOND_RATIO
        self.DAY_FRAMES = self.HOUR_FRAMES * env.DAY_HOUR_RATIO
        self.MONTH_FRAMES = self.DAY_FRAMES * env.MONTH_DAY_RATIO
        self.SEASON_FRAMES = self.MONTH_FRAMES * env.SEASON_MONTH_RATIO
        self.YEAR_FRAMES = self.SEASON_FRAMES * env.YEAR_SEASON_RATIO
        env.HOUR_FRAMES = self.HOUR_FRAMES
        env.DAY_FRAMES = self.DAY_FRAMES
        env.MONTH_FRAMES = self.MONTH_FRAMES

    def reset(self):
        self._reset_map()
        self._refresh_init()

    def _reset_map(self):
        env_map = self._env.map
        env_map.reset(map_cfg)

    def update(self):
        # first update timer
        frames = self._env.frames + 1
        self._env.frames += 1
        for player in self._env.players:
            player.update()

        for animal in self._env.animals:
            animal.update()

        for plant in self._env.plants:
            plant.update()

        self._env.players = [p for p in self._env.players if p.hp > 0]
        self._env.animals = [p for p in self._env.animals if p.hp > 0]
        self._env.plants = [p for p in self._env.plants if p.hp > 0]

        self._update_timer(frames)

    def _update_timer(self, frames):
        if frames % self.FRAME_RATE == 0:
            self.on_second_elapse(frames // self.FRAME_RATE)

        day = frames // self.DAY_FRAMES
        day_residual, day_change = frames % self.DAY_FRAMES, frames % self.DAY_FRAMES == 0
        if day_change:
            month, month_change = day // 30, day % 30 == 0
            if month_change:
                # logging.info(" a new month begin ... ")
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

    def _refresh_init(self):
        self._refresh_init_players()
        self._refresh_init_animals()
        self._refresh_init_plants()

    def _refresh_init_players(self):
        env_map = self._env.map
        self._env.players = []
        cells = env_map.select_cells(string2terrains("SELF_HOUSE"))
        for cell in cells:
            y = cell.y
            x = cell.x
            player = make_player(self._env)
            player.position = ((x + 0.5) * env_map.cell_size, (y + 0.5) * env_map.cell_size)
            logging.warning(f"spawn a {player.get_name()} at cell {cell.x},{cell.y}, "
                            f"position ({player.position[0]},{player.position[1]})")
            self._env.players.append(player)
            cell.move_in(player)

    def _refresh_init_animals(self):
        self._env.animals = []
        self._refresh_animals()

    def _refresh_animals(self):
        from env.animals import animal_cfg
        residuals = {}
        for species, cfg in animal_cfg.items():
            residuals[species] = 0

        for animal in self._env.animals:
            if animal.hp > 0:
                residuals[animal.species] += 1

        for species, cfg in animal_cfg.items():
            need_cnt = cfg["init_count"] - residuals[species]
            cells = self._env.map.select_cells(string2terrains(cfg["terrains"]), size=need_cnt)
            self._refresh_animals_species(species, cells)

    def _refresh_init_plants(self):
        self._env.plants = []
        self._refresh_plants()

    def _refresh_plants(self):
        from env.plants import plant_cfg
        residuals = {}
        for species, cfg in plant_cfg.items():
            residuals[species] = 0

        for plant in self._env.plants:
            residuals[plant.species] += 1

        for species, cfg in plant_cfg.items():
            need_cnt = cfg.init_count - residuals[species]
            cells = self._env.map.select_cells(string2terrains(cfg.terrains), size=need_cnt)
            self._refresh_plants_species(species, cells)

    def _refresh_animals_species(self, species, cells):
        for cell in cells:
            sp = new_animal(species, self._env)
            pos_x, pos_y = self._env.map.get_cell_center(cell)
            sp.position = np.array([pos_x, pos_y])
            cell.spawn_animal(sp)
            logging.info(f"spawn a {species} at cell {cell.x},{cell.y}"
                         f" position ({pos_x},{pos_y})")
            self._env.animals.append(sp)

    def _refresh_plants_species(self, species, cells):
        from env.plants import new_plant
        for cell in cells:
            sp = new_plant(species, self._env)
            pos_x, pos_y = self._env.map.get_cell_center(cell)
            sp.position = np.array([pos_x, pos_y])
            cell.spawn_plant(sp)
            logging.info(f"spawn a {species} at cell {cell.x},{cell.y}  "
                         f"position ({pos_x},{pos_y})")
            self._env.plants.append(sp)

    def on_new_day(self, _):
        for player in self._env.players:
            player.on_new_day()
        self._refresh_animals()
        self._refresh_plants()

    def on_sun_raise(self, day):
        msg = f"day event sun raise ... day {day}"
        logging.debug(msg)
        self._env.message.append(msg)

    def on_noon(self, day):
        msg = f"day event the noon ... day {day}"
        logging.debug(msg)
        self._env.message.append(msg)

    def on_sun_sink(self, day):
        msg = f"day event the run sink ... day {day}"
        logging.debug(msg)
        self._env.message.append(msg)

    def on_second_elapse(self, _):
        assert self is not None
        # logging.debug(f"second elapse ... {event}")

    def on_season_change(self, new_season):
        assert self is not None
        msg = f" a new season begin ... season {new_season}"
        logging.debug(msg)
        self._env.message.append(msg)

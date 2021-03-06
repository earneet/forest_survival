from typing import List, Sequence, Tuple

import math
import numpy as np
from munch import DefaultMunch
from random import shuffle

from env.common import Terrain
from .import MapCell


class Map:
    def __init__(self, x=20, y=20, cell_size=20.0):
        self.cell_x = x
        self.cell_y = y
        self.cell_size = cell_size
        self.cells: List[MapCell] = [MapCell(x, y) for y in range(self.cell_y) for x in range(self.cell_x)]

    def select_cells(self, terrains, size=1, empty=True, random=True):
        terrains = terrains if isinstance(terrains, list) else [terrains]
        cells = list(self.cells)
        if random:
            shuffle(cells)
        if empty:
            return list(filter(lambda c: c.type in terrains and c.is_empty(), cells))[:size]
        else:
            return list(filter(lambda c: c.type in terrains, cells))[:size]

    def get_cell(self, x, y):
        if x < 0 or y < 0 or x >= self.cell_x or y >= self.cell_y:
            return None
        return self.cells[y * self.cell_x + x]

    def pos_2_xy(self, pos):
        assert (isinstance(pos, Sequence) or isinstance(pos, np.ndarray)) and len(pos) == 2
        pos_x, pos_y = pos
        return math.floor(pos_x / self.cell_size), math.floor(pos_y / self.cell_size)

    def get_cell_by_pos(self, pos):
        x, y = self.pos_2_xy(pos)
        return self.get_cell(x, y)

    def get_round_cells_by_pos(self, pos, scope=1):
        x, y = self.pos_2_xy(pos)
        return self.get_round_cells(x, y, scope)

    def get_round_cells(self, x, y, scope=1):
        cells = []
        for iy in range(max(0, y-scope), min(y + scope + 1, self.cell_y)):
            for ix in range(max(0, x-scope), min(x + scope + 1, self.cell_x)):
                cells.append(self.get_cell(ix, iy))
        return cells

    def get_cell_edge(self, cell) -> Tuple[float, float, float, float]:
        """
        get cell's edge by cell object

        Args:
            cell: map cell object, the cell must in the same map

        Returns:
            edge limit, a tuple of four, (left, right, bottom, top)
        """
        assert isinstance(cell, MapCell) and isinstance(cell.x, int) and isinstance(cell.y, int)
        x, y = cell.x, cell.y
        assert 0 <= x < self.cell_x and 0 <= y < self.cell_y, "cell invalid"
        return x * self.cell_size, (x+1) * self.cell_size - 1, (y+1) * self.cell_size - 1, y * self.cell_size

    def get_cell_center(self, cell) -> Tuple[float, float]:
        """
        get cell center position by cell object

        Args:
            cell: target map cell object

        Returns:
            position: cell center position, a tuple of two integer(float)
        """
        assert isinstance(cell, MapCell) and isinstance(cell.x, int) and isinstance(cell.y, int)
        x, y = cell.x, cell.y
        assert 0 <= x < self.cell_x and 0 <= y < self.cell_y, "cell invalid"
        return (x + 0.5) * self.cell_size, (y+0.5) * self.cell_size

    def reset(self, cfg):
        cfg = DefaultMunch.fromDict(cfg) if isinstance(cfg, dict) else cfg
        self.cell_x = cfg.cell_x
        self.cell_y = cfg.cell_y
        self.cell_size = cfg.cell_size
        self.cells = []
        data = cfg.data
        assert len(data) == self.cell_x * self.cell_y, "map config size not match, " \
                                                       "data size should equals cell_x * cell_y"
        for y in range(self.cell_y):
            for x in range(self.cell_x):
                terrain = data[y * self.cell_x + x]
                self.cells.append(MapCell(x, y, Terrain(int(terrain))))

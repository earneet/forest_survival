from queue import PriorityQueue
from typing import List, Optional

from env.map import MapCell, Map

class AStarCell:
    def __init__(self, cell: MapCell, g: float, h: float, pre):
        self.cell = cell
        self.pre = pre
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        if not isinstance(other, AStarCell):
            return False
        if self.f == other.f:
            return self.g < other.g
        else:
            return self.f < other.f


def a_star(game_obj, start: MapCell, destination: MapCell, world_map: Map):
    open_set = PriorityQueue()
    visited = set()

    def get_neighbors(cell) -> List[MapCell]:
        x, y = cell.x, cell.y
        neighbors_ = [world_map.get_cell(x - 1, y), world_map.get_cell(x, y - 1),
                      world_map.get_cell(x + 1, y), world_map.get_cell(x, y + 1)]
        return list(filter(lambda c: c and c.can_move_in(game_obj) and c not in visited, neighbors_))

    def make_astar_cell(cell: MapCell, pre: Optional[AStarCell]) -> AStarCell:
        g = pre.g + 1 if pre else 1
        h = abs(destination.x - cell.x) + abs(destination.y - cell.y)
        _astar_cell = AStarCell(cell, g, h, pre)
        return _astar_cell

    start_cell = make_astar_cell(start, None)
    open_set.put([start_cell.f, start_cell])
    end = None
    while open_set:
        cur = open_set.get()[1]
        visited.add(cur.cell)
        neighbors = get_neighbors(cur.cell)
        for n in neighbors:
            if n == destination:
                end = cur
                break
            astar_cell = make_astar_cell(n, cur)
            open_set.put((astar_cell.f, astar_cell))
        if end:
            break

    result = [destination]
    while end:
        result.append(end.cell)
        end = end.pre
    result.reverse()
    return result

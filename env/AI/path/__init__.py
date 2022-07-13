from .find_path import a_star


find_path_solvers = {
    "a_star": a_star
}


def find_path(game_obj, start, end, world_map, algorithm="a_star"):
    return find_path_solvers[algorithm](game_obj, start, end, world_map)


__all__ = ["find_path"]


import logging

from env import Env
from env.AI.path import find_path


root_logger = logging.root
root_logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logging.debug("Starting ... ")
    env = Env(render=True)
    env.reset()

    res = find_path(env.players[0], env.map.get_cell(10, 10), env.map.get_cell(15, 15), env.map)
    for c in res:
        print((c.x, c.y))

import logging
import sys

print(sys.path)
from env import Env


root_logger = logging.root
root_logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logging.debug("Starting ... ")
    env = Env(render=True)
    env.reset()
    # env.render()

    logging.debug("Ready to go ... ")
    while True:
        env.step(0)

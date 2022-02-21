import logging

from env import Env

root_logger = logging.root
root_logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logging.debug("Starting ... ")
    env = Env()
    env.reset()
    # env.render()

    steps = 10000
    logging.debug("Ready to go ... ")
    while steps > 0:
        env.step(0)
        steps -= 1



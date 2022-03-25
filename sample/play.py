import logging

from env import Env


root_logger = logging.root
root_logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logging.debug("Starting ... ")
    env = Env(render=True)
    env.reset()

    logging.debug("Ready to go ... ")
    while True:
        env.step(0)
        if not env.players or env.players[0].is_dead():
            break

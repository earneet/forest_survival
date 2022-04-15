import logging
from os import path

from env import Env


root_logger = logging.root
root_logger.setLevel(logging.INFO)

if __name__ == "__main__":
    logging.debug("Starting ... ")
    parent_dir = path.dirname(__file__)
    logging.info(parent_dir)
    env = Env(render=False)

    logging.debug("Ready to go ... ")
    for i in range(50):
        env.reset()
        with open(path.join(parent_dir, "..", "logs", f"log_{i}.log"), "w") as f:
            while True:
                env.step(0)
                obs = env.observe()
                f.write(obs)
                f.write("\n")
                if not env.players or env.players[0].is_dead():
                    break

from .player import Player
from ..common import init_cfg


def make_player(env):
    idx = len(env.players)
    config = init_cfg.players
    assert idx < len(config), "init.json players list not enough"
    return Player(env, config[idx])

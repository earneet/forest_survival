def make_logic(player):
    from .player_logic import PlayerLogic
    return PlayerLogic(player)


__all__ = ['make_logic']

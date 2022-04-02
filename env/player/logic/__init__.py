from .player_common_logic import get_comfortable_temperatures, diff_materials, find_clothes

def make_logic(player):
    from .player_logic import PlayerLogic
    return PlayerLogic(player)


__all__ = ['make_logic', 'get_comfortable_temperatures', 'diff_materials', 'find_clothes']

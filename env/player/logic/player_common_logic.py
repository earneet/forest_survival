import itertools
from typing import Tuple, List, Dict

from env.items import clothes_cfg
from env.items.item import get_recipe_materials


def get_comfortable_temperatures() -> Tuple[float, float]:
    return 10, 30

def material_enough(player, item, handy=True) -> bool:
    """
    check if it has enough materials to make an {item}
    Args:
        player: Player object
        item: A equipment or cloth name
        handy: Only check handy materials if it's True, else handy and home box materials

    Returns:
        bool: True if it has enough materials to make, else False.
    """
    recipe = get_recipe_materials(item)
    assert recipe, f"Have no item {item} to make"
    return check_materials(player, recipe, handy)


def diff_materials(player, wants, only_handy=True) -> Dict[str, int]:
    """ Get the difference materials between wants and player ownerd

    Args:
        player: player object
        wants: total wants materials
        only_handy: only check handy if True else check handy and home box

    Returns:
        Dict[str, int]: the difference materials
    """
    all_items = player.handy_items if only_handy else itertools.chain(player.handy_items, player.home_items)
    material_diff = wants.copy()
    for item, cnt in all_items:
        item_name = item[0] if isinstance(item[0], str) else item[0].name()
        if item_name in material_diff:
            material_diff[item_name] -= min(cnt, material_diff[item_name])
            if material_diff[item_name] <= 0:
                del material_diff[item_name]
    return material_diff


def find_clothes(low, high) -> List[str]:
    """
    Find all clothes whose effect temperature between low and high

    Args:
        low: delta temperature floor
        high: delta temperature ceiling

    Returns:
        List[str]: a list contains all clothes matched, if no matched find, an empty list
    """
    low, high = min(low, high), max(low, high)
    matched = []
    for name, cfg in clothes_cfg.items():
        if low <= cfg.effect.temperature <= high:
            matched.append(name)
    return matched

def check_materials(player, materials, handy=True) -> bool:
    """
    check if the player has enough materials

    Args:
        player: Player object
        materials: A Dict[str, int] object, where it's key represent material name and value represent it's count
        handy: A bool value, only check handy item if it's True, else check handy and home box.

    Returns:
        bool: True, if it has enough materials else False.
    """
    haven = {}
    items = player.handy_items if handy else player.home_items
    for s, cnt in items:
        if s is None or cnt == 0:
            continue
        if not isinstance(s, str):
            s = s.name()
        if s not in haven:
            haven[s] = cnt
        else:
            haven[s] += cnt
    for name, cnt in materials.items():
        if name not in haven or cnt > haven[name]:
            return False
    return True

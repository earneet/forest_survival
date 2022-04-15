import json
from typing import Dict

from env.items.item import Equip, Cloth
from env.plants import Plant


def marshal_slot(item):
    item_obj = item[0]
    if not item_obj:
        return {}
    name = item_obj if isinstance(item_obj, str) else item_obj.name()
    wear = item_obj.wear if not isinstance(item_obj, str) else 0
    item_type = "common"
    if isinstance(item_obj, Equip):
        item_type = "equip"
    elif isinstance(item_obj, Cloth):
        item_type = "cloth"

    item_data = {
        "item_type": item_type,
        "name": name,
        "cnt": item[1],
        "wear": wear
    }
    return item_data


def marshal_equip(equip):
    if not equip:
        return {}

    item_type = "common"
    if isinstance(equip, Equip):
        item_type = "equip"
    elif isinstance(equip, Cloth):
        item_type = "cloth"
    return {
        "item_type": item_type,
        "name": equip.name(),
        "wear": equip.wear
    }


def marshal_player(player) -> Dict:
    player_data = {
        "id": player.id,
        "hp": player.hp,
        "max_hp": player.hp_max,
        "state": int(player.state) if player.state else 0,
        "sub_state": int(player.sub_state) if player.sub_state else 0,
        "position": (player.position[0], player.position[1]),
        "direction": int(player.direction),
        "goal": player.cur_goal,
        "sub_goal": player.cur_sub_goal,
        "equips": {},
        "handy": [],
        "home": [],
        "target": "e_0"
    }

    if player.interact_target:
        interact_target = player.interact_target
        candidates = player.env.plants if isinstance(interact_target, Plant) else player.env.animals
        for i, p in enumerate(candidates):
            if interact_target == p:
                player_data["target"] = f"p_{i}"
                break
    handy = []
    for h in player.handy_items:
        if h[0] and h[1] > 0:
            handy.append(marshal_slot(h))
    player_data["handy"] = handy

    home = []
    for h in player.home_items:
        if h[0] and h[1] > 0:
            home.append(marshal_slot(h))
    player_data["home"] = home

    equips = []
    for e in player.equips:
        equips.append(marshal_equip(e))
    player_data["equips"] = equips

    return player_data


def marshal_animal(animal) -> Dict:
    animal_data = {
        "species": animal.species,
        "hp": animal.hp,
        "position": (animal.position[0], animal.position[0]),
        "direction": int(animal.direction)
    }
    return animal_data


def marshal_plant(plant):
    plant_data = {
        "species": plant.species,
        "hp": plant.hp,
        "position": (plant.position[0], plant.position[1])
    }
    return plant_data


def marshal_global(env):
    global_data = {
        "player_size": len(env.players),
        "animal_size": len(env.animals),
        "plant_size": len(env.plants),
        "temperature": env.get_global_temperature(),
        "season": env.season
    }
    return global_data


def marshal(env):
    data = {}
    data["glo_info"] = marshal_global(env)
    data["players"] = [marshal_player(player) for player in env.players]
    data["animals"] = [marshal_animal(animal) for animal in env.animals]
    data["plants"] = [marshal_plant(plant) for plant in env.plants]
    log_str = json.dumps(data)
    return log_str

from os import path
import json
from typing import List, Dict

import numpy as np

from deepselector.constant import get_equip_id, item_cnt, common_item_one_hot, \
    equip_item_one_hot, cloth_item_one_hot, invalid_item_one_hot, animal_species_one_hots, plant_species_one_hots, \
    sub_goal_2_idx
from env.common import PlayerState, MoveType, DirectionEnum
from env.common.season import Season

parent_dir = path.dirname(__file__)
log_dir = path.join(parent_dir, "..", "logs")

OneHot = List[float]


def get_player_state_one_hot(state: int) -> OneHot:
    sd = [0.0 for _ in PlayerState]
    sd[state] = 1.0
    return sd


def get_player_substate_one_hot(sub_state: int) -> OneHot:
    ssd = [0.0 for _ in MoveType]
    ssd[sub_state] = 1.0
    return ssd


def get_direction_one_hot(direction) -> OneHot:
    dd = [0.0 for _ in DirectionEnum]
    dd[direction] = 1.0
    return dd


def get_equip_one_hot(name) -> OneHot:
    e_h = [0.0] * item_cnt
    e_h[get_equip_id(name)] = 1.0
    return e_h


def get_season_one_hot(season) -> OneHot:
    sd = [0.0 for _ in Season]
    sd[season] = 1.0
    return sd


def get_item_type_one_hot(item_type) -> OneHot:
    if item_type == "common":
        return common_item_one_hot
    elif item_type == "equip":
        return equip_item_one_hot
    elif item_type == "cloth":
        return cloth_item_one_hot
    return invalid_item_one_hot


def get_animal_species_one_hot(species) -> OneHot:
    return animal_species_one_hots[species]


def get_plant_species_one_hot(species) -> OneHot:
    return plant_species_one_hots[species]


def get_equips(equip) -> List[float]:
    equip_data = []
    equip_data.extend(get_item_type_one_hot(equip["item_type"]))  # item_type one hot [3]
    equip_data.extend(get_equip_one_hot(equip["name"]))  # item_id one hot [item_cnt]
    equip_data.append(equip["wear"])  # wear scalar   [1]
    equip_data.append(1.0)  # count scalar  [1]
    return equip_data


empty_equip_one_hot = [0.0] * (3 + item_cnt + 1 + 1)


def get_empty_equips() -> List[float]:
    return empty_equip_one_hot


def get_equips_data(equips: List[Dict]) -> List[float]:
    ed = []
    for equip in equips:
        if equip:
            ed.append(1.0)  # enabled flag
            ed.extend(get_equips(equip))
        else:
            ed.append(0.0)  # enabled flag
            ed.extend(get_empty_equips())
    return ed


def get_player_data(player):
    pd = [1, player["id"], player["hp"], player["max_hp"]]  # indicate this section is valid
    pd.extend(get_player_state_one_hot(player["state"]))
    pd.extend(get_player_substate_one_hot(player["sub_state"]))
    pd.extend(player["position"])
    pd.extend(get_direction_one_hot(player["direction"]))
    pd.extend(get_equips_data(player["equips"]))
    return pd


empty_animal_ = tuple([0.0] * 12)
empty_plants_ = tuple([0.0] * 7)


def empty_animal_data():
    return empty_animal_

def empty_plant_data():
    return empty_plants_

def get_animal_data(animal) -> List[float]:
    ad = []
    ad.extend(get_animal_species_one_hot(animal["species"]))
    ad.append(animal["hp"])
    ad.extend(animal["position"])
    ad.extend(get_direction_one_hot(animal["direction"]))
    return ad


def get_plant_data(plant) -> List[float]:
    pd = []
    pd.extend(get_plant_species_one_hot(plant["species"]))  # species one_hot
    pd.append(plant["hp"])      # hp
    pd.extend(plant["position"])
    return pd


def get_global_data(frame):
    gd = [frame["temperature"]]
    gd.extend(get_season_one_hot(frame["season"]))
    return gd


def get_frame_data(frame):
    glo_info = get_global_data(frame["glo_info"])
    # assert len(frame["players"]) == 2, f" players size expect 2 but got {len(frame['players'])}"

    players = []
    for player in frame["players"]:
        players.extend(get_player_data(player))
    if len(frame["players"]) == 1:
        players.extend(get_player_data(frame["players"][0]))

    max_animal_size = 10
    _animals = frame["animals"][:max_animal_size + 1]
    animals = []
    for animal in _animals:
        animals.extend(get_animal_data(animal))
    diff = max_animal_size - len(_animals)
    if diff > 0:
        for i in range(diff):
            animals.extend(empty_animal_data())

    plants = []
    max_plant_size = 10
    _plants = frame["plants"][:max_plant_size + 1]
    for plant in _plants:
        plants.extend(get_plant_data(plant))
    diff = max_plant_size - len(_plants)
    if diff > 0:
        for i in range(diff):
            plants.extend(empty_plant_data())
    np_array = [*glo_info, *players, *animals, *plants]
    return np.array(np_array, dtype=np.float32).flatten()


def load_data_file(i):
    datas = []
    with open(path.join(log_dir, f"log_{i}.log"), "r") as f:
        for line in f.readlines():
            data = load_data(line)
            if data:
                datas.append(data)
    return datas

def load_data(line):
    data = json.loads(line)
    if len(data["players"]) < 2:
        return None
    sub_goal = data["players"][0]["sub_goal"]
    if not sub_goal:
        sub_goal = "Idle"
    label = sub_goal_2_idx[sub_goal]
    array = get_frame_data(data)
    if len(array) != 302:
        return None
    return array, label


if __name__ == "__main__":
    load_data_file(0)

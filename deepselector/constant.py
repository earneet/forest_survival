from env.common import animal_cfg, plant_cfg
from env.items import equip_cfg, clothes_cfg, prop_cfg

equip_name_2_idx = {}
clothes_name_2_idx = {}
common_name_2_idx = {}
animal_species_2_idx = {}
plant_species_2_idx = {}
sub_goal_2_idx = {}
animal_species_one_hots = {}
plant_species_one_hots = {}

sub_goals = ["Idle", "CollectingEquip", "CollectingFood", "CollectingForMaterials", "CollectingHerb", "EatingHandy",
             "EatingHome", "EquipOrMakeEquipment", "SubGoalGoHome", "Hunting", "MakeClothes", "WearClothes"]

goal_idx = 1
for sg in sorted(sub_goals):
    if sg == "Idle":
        continue
    sub_goal_2_idx[sg] = goal_idx
    goal_idx += 1

sub_goal_2_idx["Idle"] = 0

print(sub_goal_2_idx)

equip_cnt = len(equip_cfg)
equip_idx = 0
for equip in sorted(equip_cfg.keys()):
    equip_name_2_idx[equip] = equip_idx
    equip_idx += 1

cloth_cnt = len(clothes_cfg)
cloth_idx = 0
for cloth in sorted(clothes_cfg.keys()):
    clothes_name_2_idx[cloth] = cloth_idx
    cloth_idx += 1

common_cnt = len(prop_cfg)
common_idx = 0
for common in sorted(prop_cfg.keys()):
    common_name_2_idx[common] = common_idx
    common_idx += 1

item_cnt = max(equip_cnt, cloth_cnt, common_cnt)

animal_idx = 0
for animal in sorted(animal_cfg.keys()):
    animal_species_2_idx[animal] = animal_idx
    one_hot = [0.0] * len(animal_cfg)
    one_hot[animal_idx] = 1.0
    animal_species_one_hots[animal] = tuple(one_hot)
    animal_idx += 1

plant_idx = 0
for plant in sorted(plant_cfg.keys()):
    plant_species_2_idx[plant] = plant_idx
    one_hot = [0.0] * len(plant_cfg)
    one_hot[plant_idx] = 1.0
    plant_species_one_hots[plant] = tuple(one_hot)
    plant_idx += 1

common_item_one_hot = (1.0, 0.0, 0.0)
equip_item_one_hot = (0.0, 1.0, 0.0)
cloth_item_one_hot = (0.0, 0.0, 1.0)
invalid_item_one_hot = (0.0, 0.0, 0.0)


def get_equip_id(name):
    return equip_name_2_idx[name]


def get_clothes_id(name):
    return clothes_name_2_idx[name]


def get_common_id(name):
    return common_name_2_idx[name]


def get_animal_id(species):
    return animal_species_2_idx[species]


def get_plant_id(species):
    return plant_species_2_idx[species]

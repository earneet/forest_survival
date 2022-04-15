import logging

from env.AI.player.goals.sub_goals.collecting_equip import CollectingEquip
from env.AI.player.goals.sub_goals.collecting_for_food import CollectingFood
from env.AI.player.goals.sub_goals.collecting_for_materials import CollectingForMaterials
from env.AI.player.goals.sub_goals.collecting_herb import CollectingHerb
from env.AI.player.goals.sub_goals.eating_handy import EatingHandy
from env.AI.player.goals.sub_goals.eating_home import EatingHome
from env.AI.player.goals.sub_goals.equip_or_make_equipment import EquipOrMakeEquipment
from env.AI.player.goals.sub_goals.gohome_rest import SubGoalGoHome
from env.AI.player.goals.sub_goals.hunting import Hunting
from env.AI.player.goals.sub_goals.idle import Idle
from env.AI.player.goals.sub_goals.make_clothes import MakeClothes
from env.AI.player.goals.sub_goals.wear_clothes import WearClothes

sub_goal_2_idx = {}
sub_goals = {}

sub_goals_dict = {
    "Idle": Idle(),
    "CollectingEquip": CollectingEquip(),
    "CollectingFood": CollectingFood(),
    "CollectingForMaterials": CollectingForMaterials(),
    "CollectingHerb": CollectingHerb(),
    "EatingHandy": EatingHandy(),
    "EatingHome": EatingHome(),
    "EquipOrMakeEquipment": EquipOrMakeEquipment(),
    "SubGoalGoHome": SubGoalGoHome(),
    "Hunting": Hunting(),
    "MakeClothes": MakeClothes(),
    "WearClothes": WearClothes()
}

goal_idx = 1
for sg in sorted(sub_goals_dict.keys()):
    if sg == "Idle":
        continue
    sub_goal_2_idx[sg] = goal_idx
    sub_goals[goal_idx] = sg
    goal_idx += 1

sub_goals[0] = "Idle"

logging.info(sub_goals)

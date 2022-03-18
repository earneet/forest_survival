from enum import IntEnum

class PlayerState(IntEnum):
    IDLE = 0  # 什么都没干
    MOVING = 1  # 在移动
    BATTLING = 2  # 在打架
    COLLECTING = 3  # 在收集
    RESTING = 4  # 在休整
    MAKING = 5  # 在制造


class SlotType(IntEnum):
    EQUIP = 0
    CLOTH = 1


WEAPON_SLOT = 0
CLOTHES_SLOT = 1

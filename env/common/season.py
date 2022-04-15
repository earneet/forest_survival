from enum import IntEnum


class Season(IntEnum):
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3
    WINTER = 4


SeasonTemperatures = {
    Season.SPRING: 25,
    Season.SUMMER: 30,
    Season.AUTUMN: 18,
    Season.WINTER: 10
}


def get_season_temperature(season):
    return SeasonTemperatures[season]

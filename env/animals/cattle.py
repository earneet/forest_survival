from typing import Dict

from ray.rllib.utils import override

from env.animals.animal import Animal


class Cattle(Animal):
    def __init__(self):
        super().__init__()

    @override
    def pecies(self):
        return "cattle"

    def drop_items(self) -> Dict[int, int]:
        return {}
import logging
import random
from typing import Dict

from env.common.event.event import CollectEnd


class Plant:
    def __init__(self, cfg, env):
        assert env is not None
        super().__init__()
        self.collectors = {}
        self.collector = None
        self.cfg = cfg
        self.hp = 1  # all plants has a default hp value 1, when it be collected, change to 0
        self.position = [0, 0]
        self._species = cfg.species
        self.env = env

    @property
    def species(self) -> str:
        return self._species

    def get_name(self):
        return self._species

    def collect(self, player, frame=None):
        if frame is None:
            frame = self.env.frames
        self.collectors[player.id] = frame

    def stop_collect(self, player):
        del self.collectors[player.id]

    def is_dead(self):
        return self.hp <= 0

    def update(self):
        if not self.collectors:
            return

        cur_frame = self.env.frames
        for p, f in self.collectors.items():
            if cur_frame - f < self.cfg.collect_time * self.env.HOUR_FRAMES:
                logging.debug(f"I am not ready  {self.cfg.collect_time * self.env.HOUR_FRAMES - (cur_frame - f)}")
                continue
            rewards = self.drop()
            collector = self.env.get_player(p)
            collector.pickup(rewards)
            self.hp = 0
            self.collector = p
            logging.warning(f" Plant was collected by {collector.get_name()}")
            break

        if self.hp == 0:
            self.on_collected()

    def on_collected(self):
        for p, f in self.collectors.items():
            collector = self.env.get_player(p)
            if collector is None or collector.is_dead():
                continue
            collector.events.append(CollectEnd(self, collector))
        self.collectors = {}

    def drop(self) -> Dict[str, int]:
        drop_items = {}
        drop_cfg = self.cfg.drop or {}
        for item, drop_cfg in drop_cfg.items():
            old_cnt = drop_items[item] if item in drop_items else 0
            cnt = 0
            if isinstance(drop_cfg, int):
                cnt = drop_cfg
            elif isinstance(drop_cfg, float):
                cnt = 1 if random.random() < drop_cfg else 0
            elif isinstance(drop_cfg, list) or isinstance(drop_cfg, tuple):
                if len(drop_cfg) >= 2:
                    cnt = random.randint(drop_cfg[0], drop_cfg[1])
                else:
                    cnt = 0
            drop_items[item] = max(cnt, 0) + old_cnt

        return drop_items

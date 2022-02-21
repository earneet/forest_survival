import math
import itertools
from typing import Optional, List

id_timer = itertools.count()
next(id_timer)


class Timer:
    def __init__(self, event_name):
        self.id = next(id_timer)
        self._last_trigger = 0
        self._next_trigger = math.inf
        self._max_trigger_times = 1
        self._event = event_name
        self._valid = True

    @property
    def last_trigger(self):
        return self._last_trigger

    @property
    def next_trigger(self):
        return self._next_trigger

    @property
    def event(self):
        return self._event

    @property
    def max_trigger_times(self):
        return self._max_trigger_times

    @property
    def valid(self):
        return self._valid

    def trigger(self, frame) -> Optional[str]:
        if frame < self._next_trigger:
            return

        if self._max_trigger_times > 0:
            self._max_trigger_times -= 1
            if self._max_trigger_times == 0:
                self._valid = False

        return self._event

    def __lt__(self, other):
        return False if other is None or isinstance(other, self.__class__) else self.id < other.id

    def __eq__(self, other):
        return False if other is None or isinstance(other, self.__class__) else id(other) == id(self)


class FixedPeriodTimer(Timer):
    def __init__(self, interval, event_name):
        super().__init__(event_name)
        self.frame_interval = interval // TimerManager.FRAME_INTERVAL

    def trigger(self, frame) -> Optional[str]:
        event = super().trigger(frame)
        if not event:
            return event

        self._next_trigger += self.frame_interval
        self._last_trigger = frame
        return event


class TimerManager:
    FRAME_RATE = 10
    FRAME_INTERVAL = 1 / FRAME_RATE

    def __init__(self):
        self._frames = 0
        self._timers = []

    def tick(self) -> List[str]:
        self._frames += 1
        events = []
        invalids = []
        for t in self._timers:
            event = t.trigger(self._frames)
            if event:
                events.append(event)
                if not t.valid():
                    invalids.append(t)
            else:
                break
        self._resort_timer()
        return events

    def remove(self, timer):
        if isinstance(timer, Timer):
            self._timers.remove(timer)
        elif isinstance(timer, int):
            self._timers = [x for x in self._timers if x.id != timer]
        else:
            raise ValueError()

    def reset(self):
        self._frames = 0
        self._timers = []

    def get_time(self):
        return self._frames

    def add_timer(self, timer):
        if isinstance(timer, Timer):
            timer = [timer]
        elif isinstance(timer, List):
            assert all(isinstance(t, Timer) for t in timer)
        else:
            raise ValueError()

        self._timers.extend(timer)
        self._resort_timer()

    def _resort_timer(self):
        self._timers.sort(key=lambda s: s.next_trigger)

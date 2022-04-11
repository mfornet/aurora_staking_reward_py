from fractions import Fraction
from typing import List, Tuple


Amount = Fraction
StreamId = int
User = int
Time = int


class Schedule:
    def __init__(self, details: List[Tuple[Time, Amount]]):
        # Validate schedule
        assert len(details) > 1
        assert details[0][0] == 0
        for d0, d1 in zip(details, details[1:]):
            assert d0[0] < d1[0]
            assert d0[1] <= d1[1]

        self.details = details

    def reward_at(self, time: Time) -> Amount:
        if time <= self.details[0][0]:
            return Amount(0)

        for i in range(1, len(self.details)):
            prev = self.details[i - 1]
            curr = self.details[i]

            if prev[0] < time <= curr[0]:
                return prev[1] + (curr[1] - prev[1]) * (time - prev[0]) / (curr[0] - prev[0])

        return self.details[-1][1]


class Timer:
    def __init__(self):
        self._now = 0

    def set(self, time: Time):
        assert time > self._now
        self._now = time

    def advance(self, delta: Time):
        self.set(self._now + delta)

    @property
    def now(self) -> Time:
        return self._now

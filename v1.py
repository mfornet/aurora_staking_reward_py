from collections import defaultdict
from common import Schedule, StreamId, Time, Timer, User, Amount
from typing import List


class StreamData:
    schedule: Schedule

    def __init__(self, schedule: Schedule):
        self.schedule = schedule

        # Rewards Per Share Accumulated
        self.rps_acc = 0

        # Rewards per share after claiming
        self.rps = defaultdict(lambda: 0)


class ContractV1:
    def __init__(self, time: Timer):
        self.time = time
        self.last_update = self.time.now

        self.streams: List[StreamData] = []

        # Shares in other pools
        self.shares = defaultdict(lambda: Amount(0))
        self.total_shares = Amount(0)

    def create_stream(self, amount: Amount, schedule: Schedule) -> StreamId:
        # Make sure this is a valid schedule
        assert schedule.details[-1][1] == amount
        assert schedule.details[0][0] >= self.time.now

        index = len(self.streams)
        self.streams.append(StreamData(schedule))

        return index

    def _update_streams(self):
        if self.total_shares != Amount(0):
            for stream in self.streams:
                delta_reward = stream.schedule.reward_at(
                    self.time.now) - stream.schedule.reward_at(self.last_update)
                stream.rps_acc += delta_reward / self.total_shares

        self.last_update = self.time.now

    def stake(self, user: User, amount: Amount):
        self._update_streams()

        # This formulae will change (depending on weight and compounding accordingly)
        self.total_shares += amount
        self.shares[user] += amount

    def unstake(self, user: User, amount: Amount):
        assert self.shares[user] >= amount

        self._update_streams()
        self.total_shares -= amount
        self.shares[user] -= amount

    def claim(self, user: User, stream_id: StreamId) -> Amount:
        reward = self.reward(user, stream_id)

        stream = self.streams[stream_id]
        stream.rps[user] = stream.rps_acc

        return reward

    def reward(self, user: User, stream_id: StreamId) -> Amount:
        self._update_streams()
        stream = self.streams[stream_id]
        return self.shares[user] * (stream.rps_acc - stream.rps[user])

    def all_rewards(self, user: User) -> Amount:
        return [self.reward(user, stream_id) for stream_id in range(len(self.streams))]

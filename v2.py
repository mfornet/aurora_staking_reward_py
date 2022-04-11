from collections import defaultdict
from common import Schedule, StreamId, Time, Timer, User, Amount
from typing import List
from heapq import heappop as pop, heappush as push


class StreamData:
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.history = []


class UserInfo:
    def __init__(self):
        self.num_shares = 0
        self.last_update = 0
        self.acc = 0
        self.acc_F_last = 0
        self.claimed = 0

        self.history = [(self.last_update, self.num_shares, self.acc)]

    def update(self, delta_shares: Amount, now: Time, acc_F: Amount):
        self.acc += (acc_F - self.acc_F_last) * self.num_shares

        self.history.append((now, self.num_shares, self.acc))

        self.num_shares += delta_shares
        assert self.num_shares >= 0
        self.acc_F_last = acc_F


class ContractV2:
    def __init__(self, time: Timer):
        self.time = time
        self.last_update = self.time.now

        # F is the integral of (1 / max(1, total_shares(t))) from the beginning of the contract to the present
        self.acc_F = 0

        # Streams
        self.streams: List[StreamData] = []

        # Next events
        self.events = []

        # Shares in other pools
        self.total_shares = Amount(0)

        self.users = defaultdict(lambda: UserInfo())

    def _update_F(self, now=None):
        if now is None:
            now = self.time.now
        assert now >= self.last_update
        self.acc_F += (now - self.last_update) / \
            max(Amount(1), self.total_shares)
        self.last_update = now

    def _update_user(self, user: User, delta: Amount):
        self.ping()
        self._update_F()
        self.users[user].update(delta, self.time.now, self.acc_F)
        self.total_shares += delta

    def ping(self):
        """
        This is an amortized function that is expected to be O(1)
        it needs to update each stream when the part of the piece-wise linear function changes.

        Anyone can call this function from the outside, and it is possible
        to call it with a parameter that specifies how many cycles will be executed.
        """

        while len(self.events) > 0 and self.events[0][0] <= self.time.now:
            time, stream_id, piece_id = pop(self.events)
            self._update_F(time)

            if len(self.streams[stream_id].schedule.details) > piece_id + 1:
                curr = self.streams[stream_id].schedule.details[piece_id]
                next = self.streams[stream_id].schedule.details[piece_id + 1]
                slope = (next[1] - curr[1]) / (next[0] - curr[0])

                self.streams[stream_id].history.append((self.acc_F, slope))

                push(self.events, (next[0], stream_id, piece_id + 1))
            else:
                self.streams[stream_id].history.append((self.acc_F, 0))

    def create_stream(self, amount: Amount, schedule: Schedule) -> StreamId:
        # Make sure this is a valid schedule
        assert schedule.details[-1][1] == amount
        assert schedule.details[0][0] >= self.time.now

        index = len(self.streams)
        push(self.events, (schedule.details[0][0], index, 0))

        self.streams.append(StreamData(schedule, self.time.now))

        return index

    def stake(self, user: User, amount: Amount):
        self._update_user(user, amount)

    def unstake(self, user: User, amount: Amount):
        self._update_user(user, -amount)

    def claim(self, user: User, stream_id: StreamId) -> Amount:
        reward = self.reward(user, stream_id)
        self.users[user].claimed += reward
        return reward

    def reward(self, user: User, stream_id: StreamId) -> Amount:
        self._update_user(user, 0)
        # TODO: Compute reward properly from stream info

    def all_rewards(self, user: User) -> Amount:
        return [self.reward(user, stream_id) for stream_id in range(len(self.streams))]

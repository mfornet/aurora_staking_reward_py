from typing import Type

from common import Amount, Schedule, Timer
from v1 import ContractV1


def simple_schedule() -> Schedule:
    return Schedule([(0, Amount(0)), (100, Amount(100))])


def test_simple(ContractCls: Type[ContractV1]):
    timer = Timer()
    contract = ContractCls(timer)
    stream_id = contract.create_stream(Amount(100), simple_schedule())
    contract.stake(0, Amount(1))
    timer.set(10)
    assert contract.reward(0, stream_id) == Amount(10)
    timer.set(20)
    assert contract.claim(0, stream_id) == Amount(20)
    timer.set(110)
    assert contract.claim(0, stream_id) == Amount(80)
    assert contract.claim(0, stream_id) == Amount(0)


def test_two_users(ContractCls: Type[ContractV1]):
    timer = Timer()
    contract = ContractCls(timer)

    si = contract.create_stream(Amount(100), simple_schedule())

    contract.stake(0, Amount(1))
    contract.stake(1, Amount(2))

    timer.set(10)
    assert contract.reward(1, si) == Amount(20) / 3
    timer.set(20)
    assert contract.claim(1, si) == Amount(40) / 3
    timer.set(110)
    assert contract.claim(1, si) == Amount(160) / 3
    assert contract.claim(1, si) == Amount(0)


if __name__ == '__main__':
    test_two_users(ContractV1)

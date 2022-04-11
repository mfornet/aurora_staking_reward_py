# Aurora Staking Contracts (Python Demo)

Quick implementation Aurora Staking contracts in Python to use as a benchmark and testing tool.

## V2

Contract V2 makes "no loop" during staking and unstaking. While claiming it needs to go through all checkpoints of the stream to compute the current reward accrued. The complexity of this operation is logarithmic in the number of operation of the user times the number of checkpoints of the stream. It is expected to work with up to 10,000 operations and 5 checkpoints.

While staking/unstaking relevant streams needs to be updated, but this is done in an amortized way, and if no malicious stream is added, it is expected that this takes constant time.

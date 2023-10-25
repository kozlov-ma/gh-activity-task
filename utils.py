import typing
from collections import Counter


def flatten(l: list[list[typing.Any]]) -> list[typing.Any]:
    return [item for sublist in l for item in sublist]


def counter_sum(counters: typing.Iterable[Counter]) -> Counter:
    ctr = Counter()
    for c in counters:
        ctr += c

    return ctr

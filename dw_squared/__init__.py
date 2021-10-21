from itertools import cycle
import collections.abc

PALETTE = cycle([7, 2, 9, 5, 6, 8, 2, 10])


def nest_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = nest_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

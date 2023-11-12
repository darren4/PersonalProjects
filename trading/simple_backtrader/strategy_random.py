import random
from simple_backtrader.constants import *

random.seed(1)


def random_long(historical_data: list, position: dict):
    num = random.randint(1, 2)
    if num == 1:
        return [(BUY, 1)]
    else:
        return [(CLOSE_BUY, 1)]


def random_short(historical_data: list, position: dict):
    num = random.randint(1, 2)
    if num == 1:
        return [(SELL, 1)]
    else:
        return [(CLOSE_SELL, 1)]

from nlp.binary_strategies.strat_base import Strategy
import numpy as np


class AllTrue(Strategy):
    def __init__(self):
        pass

    def train(self, X, y):
        pass

    def predict(self, X):
        return np.full((len(X), 1), True)


class AllFalse(Strategy):
    def __init__(self):
        pass

    def train(self, X, y):
        pass

    def predict(self, X):
        return np.full((len(X), 1), False)

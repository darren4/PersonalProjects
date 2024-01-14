from nlp.binary_strategies.strat_base import Strategy
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import numpy as np


def char_intersect(s0, s1):
    return len(set(s0).intersection(s1)) / (len(s0) + len(s1))


class Simple(Strategy):
    def __init__(self):
        self.decision_tree = DecisionTreeClassifier(max_depth=2)

    def _convert_string_pair(self, s0, s1):
        return char_intersect(s0, s1)

    def _convert_row(self, row):
        return self._convert_string_pair(row[0], row[1])

    def _convert_input_array(self, X):
        X = np.apply_along_axis(self._convert_row, 1, X)
        return np.reshape(X, (-1, 1))

    def train(self, X, y):
        X = self._convert_input_array(X)
        self.decision_tree.fit(X, y)

    def predict(self, X):
        X = self._convert_input_array(X)
        return self.decision_tree.predict(X)

from nlp.binary_strategies.strat_base import Strategy
import numpy as np
from sklearn.neural_network import MLPClassifier
import sys


class ManualWordEmbeddings(Strategy):
    def __init__(self):
        self.next_word_val = 1
        self.word_vals = {}
        self.max_sentence_len = 0
        # self.classifier = MLPClassifier(hidden_layer_sizes=(16, 8, 4), max_iter=500)
        self.classifier = MLPClassifier(max_iter=500)

    def _add_to_word_vals(self, s_list):
        for w in s_list:
            if w not in self.word_vals:
                self.word_vals[w] = self.next_word_val
                self.next_word_val += 1

    def _process_raw_row(self, row):
        s0 = row[0]
        s1 = row[1]
        s0 = s0.split()
        s1 = s1.split()
        self.max_sentence_len = max(self.max_sentence_len, len(s0), len(s1))
        self._add_to_word_vals(s0)
        self._add_to_word_vals(s1)
        return row

    def _apply_word_embeddings(self, row):
        x_arr = np.zeros((self.max_sentence_len * 2))
        row[0] = row[0].split()
        for i in range(len(row[0])):
            try:
                x_arr[i] = self.word_vals[row[0][i]]
            except KeyError:
                x_arr[i] = 0
        row[1] = row[1].split()
        for i in range(len(row[1])):
            try:
                try:
                    x_arr[i + self.max_sentence_len] = self.word_vals[row[1][i]]
                except KeyError:
                    x_arr[i + self.max_sentence_len] = 0
            except IndexError:
                break
        return x_arr

    def train(self, X, y):
        X = np.apply_along_axis(self._process_raw_row, 1, X)
        X = np.apply_along_axis(self._apply_word_embeddings, 1, X)
        self.classifier.fit(X, y)

    def predict(self, X):
        X = np.apply_along_axis(self._apply_word_embeddings, 1, X)
        return self.classifier.predict(X)

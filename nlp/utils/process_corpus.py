from utils.cleaning import sentence_to_list
from nlp.utils.list_normalization import adjust_list_len

import numpy as np
import pandas as pd


class StringsToVectors:
    def __init__(self, _word_vector_dict, _embed_len):
        self.max_len = 0
        self.word_vector_dict = _word_vector_dict
        self.unknown_vector_missing = "<unk>" not in self.word_vector_dict
        self.embed_len = _embed_len
        self.process_columns = None

        self.total_tokens = 0
        self.unknown_token_count = 0

    def to_vector(self, string: str) -> np.array:
        words = sentence_to_list(string)
        self.max_len = max(len(words), self.max_len)
        vectors = []
        self.total_tokens += len(words)
        for i in range(len(words)):
            try:
                vectors.append(self.word_vector_dict[words[i]])
            except KeyError:
                self.unknown_token_count += 1
                try:
                    vectors.append(self.word_vector_dict["<unk>"])
                except KeyError:
                    vectors.append(np.zeros(self.embed_len))

        if not vectors:
            vectors = [np.zeros(self.embed_len)]
        return np.array(vectors)

    def _process_row(self, row):
        for corpus_col, mat_col in self.process_columns.items():
            row[mat_col] = self.to_vector(row[corpus_col])
        return row

    def to_vectors(self, df: pd.DataFrame, _process_columns: dict) -> tuple:
        self.process_columns = _process_columns
        return df.apply(self._process_row, axis=1), self.max_len

    def last_unknown_prop(self):
        prop = self.unknown_token_count / self.total_tokens
        self.unknown_token_count = 0
        self.total_tokens = 0
        return prop


class NormalizeVectorLens:
    def __init__(self, _target_len, _embed_len, strategy="ADJUST_LEN"):
        """
        strategy can be "ADJUST_LEN" or "AVG_SEMANTICS"
        """
        self.target_len = _target_len
        self.embed_len = _embed_len
        if strategy == "ADJUST_LEN":
            self.noramlize = self._adjust_vector_lens
        elif strategy == "AVG_SEMANTICS":
            self.noramlize = self._avg_semantics
        else:
            raise ValueError(f"Unidentified strategy: {strategy}")

    def _adjust_vector_lens(self, matrix: np.array) -> np.array:
        matrix_adjusted = np.zeros((self.target_len, self.embed_len))
        for i in range(self.embed_len):
            vector = list(matrix[:, i])
            vector = adjust_list_len(vector, self.target_len)
            matrix_adjusted[:, i] = np.array(vector)
        return matrix_adjusted

    def _avg_semantics(self, matrix: np.array) -> np.array:
        return np.mean(matrix, axis=0)

    def normalize(self, matrix: np.array) -> np.array:
        """
        Matrix is 2d matrix (word, word semantics vector)
        """
        raise NotImplementedError()

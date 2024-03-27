from utils.string_cleaning import sentence_to_list
from nlp.vectorize.vectorize_with_embeddings.vectorize_with_embeddings.list_normalization import adjust_list_len
from nlp.vectorize.base_vectorize import BaseVectorize

import numpy as np
from typing import List


def normalize_adjust_lens(
    matrix: np.array, target_len: int, embed_len: int
) -> np.array:
    matrix_adjusted = np.zeros((target_len, embed_len))
    for i in range(embed_len):
        vector = list(matrix[:, i])
        vector = adjust_list_len(vector, target_len)
        matrix_adjusted[:, i] = np.array(vector)
    return matrix_adjusted


def normalize_avg_semantics(matrix: np.array) -> np.array:
    return np.mean(matrix, axis=0)


class VectorizeWithDict(BaseVectorize):
    def __init__(self, word_vector_dict, embed_len):
        self._max_len = 0
        self._word_vector_dict = word_vector_dict
        self._unknown_vector_missing = "<unk>" not in self._word_vector_dict
        self._embed_len = embed_len

        self._total_tokens = 0
        self._unknown_token_count = 0

    def _string_to_vector(self, string: str) -> np.array:
        words = sentence_to_list(string)
        self._max_len = max(len(words), self._max_len)
        vectors = []
        self._total_tokens += len(words)
        for i in range(len(words)):
            try:
                vectors.append(self._word_vector_dict[words[i]])
            except KeyError:
                self._unknown_token_count += 1
                try:
                    vectors.append(self._word_vector_dict["<unk>"])
                except KeyError:
                    vectors.append(np.zeros(self._embed_len))

        if not vectors:
            vectors = [np.zeros(self._embed_len)]
        return np.array(vectors)

    def vectorize(self, strings: List[str]) -> List[np.array]:
        vectorized = [self._string_to_vector(string) for string in strings]
        return [
            normalize_adjust_lens(matrix, self._max_len, self._embed_len)
            for matrix in vectorized
        ]

    def last_unknown_prop(self):
        prop = self._unknown_token_count / self._total_tokens
        self._unknown_token_count = 0
        self._total_tokens = 0
        return prop

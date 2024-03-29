from nlp.vectorize.lib.list_normalization import (
    adjust_list_len,
)
from nlp.vectorize.base_vectorize import BaseVectorize
from nlp.vectorize.lib.build_glove_embeddings.fine_tune_embeddings import (
    fine_tune_embeddings,
)
from nlp.vectorize.lib.build_glove_embeddings.glove.GloVeProcessor import GloVeProcessor

import numpy as np
from typing import List, Dict, Sequence


class VectorizeWithGloVe(BaseVectorize):
    def __init__(
        self,
        corpus: List[str],
        embed_len: int = 10,
        window_len: int = 3,
        pretrained_vectors: Dict[str, Sequence] = None,
    ):
        self._embed_len = embed_len
        self._window_len = window_len
        processed_corpus = [string.lower() for string in corpus]
        if pretrained_vectors:
            processed_corpus_lists = [string.split() for string in processed_corpus]
            self._word_vector_dict = fine_tune_embeddings(
                pretrained_vectors, processed_corpus_lists, self._embed_len
            )
        else:
            self._word_vector_dict = GloVeProcessor(
                self._embed_len, self._window_len
            ).train_glove_vectors(processed_corpus)

    def _normalize_adjust_lens(
        matrix: np.array, target_len: int, embed_len: int
    ) -> np.array:
        matrix_adjusted = np.zeros((target_len, embed_len))
        for i in range(embed_len):
            vector = list(matrix[:, i])
            vector = adjust_list_len(vector, target_len)
            matrix_adjusted[:, i] = np.array(vector)
        return matrix_adjusted

    def _string_to_vector(self, string: str) -> np.array:
        words = string.lower().split()
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
            self._normalize_adjust_lens(matrix, self._max_len, self._embed_len)
            for matrix in vectorized
        ]

    def last_unknown_prop(self):
        prop = self._unknown_token_count / self._total_tokens
        self._unknown_token_count = 0
        self._total_tokens = 0
        return prop

from typing import Final, Tuple, List
import numpy as np


INDEX_RANGE: Final[Tuple[int, int]] = (-100, 100)

class MultiDimSearch:
    def __init__(self, emedding_vector_len: int, corpus_embed_str_list: List[Tuple[np.array, str]]):
        self._embedding_vector_len = emedding_vector_len

        self._index = np.empty((self._embedding_vector_len, INDEX_RANGE[1] - INDEX_RANGE[0] + 1), dtype=object)
        for r in range(self._index.shape[0]):
            for c in range(self._index.shape[1]):
                self._index[r, c] = []

        self._corpus = []
        for corpus_idx in range(len(corpus_embed_str_list)):
            embed_vector, doc = corpus_embed_str_list[corpus_idx]
            self._corpus.append(doc)
            for embed_idx in range(self._embedding_vector_len):
                norm_embed = self._normalize_embed_value(embed_vector[embed_idx])
                self._index[embed_idx, norm_embed].append(corpus_idx)
                print(f"Added {corpus_idx} to ({embed_idx}, {norm_embed})")


    def _normalize_embed_value(self, embed_value: float) -> int:
        norm_value = int(int(embed_value * INDEX_RANGE[1]) + INDEX_RANGE[1])
        assert(embed_value >= 0)
        return norm_value


        


from typing import Final, Tuple, List
import numpy as np


NORM_EMBED_RANGE: Final[Tuple[int, int]] = (-100, 100)
DEFAULT_MAX_RESULT_COUNT: Final[int] = 5
SEARCH_DISTANCE: Final[int] = 10
COVERED_EMBED_CUTOFF_PROP: Final[float] = 0.7


class CoverageSearch:
    def __init__(
        self,
        corpus_embed_str_list: List[Tuple[np.array, str]],
        emedding_vector_len: int,
    ):
        self._embedding_vector_len = emedding_vector_len

        self._search_range = NORM_EMBED_RANGE[1] - NORM_EMBED_RANGE[0] + 1
        self._max_index = self._search_range - 1

        self._index = np.empty(
            (self._embedding_vector_len, self._search_range), dtype=object
        )
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

    def _normalize_embed_value(self, embed_value: float) -> int:
        norm_value = int(embed_value * NORM_EMBED_RANGE[1]) + NORM_EMBED_RANGE[1]
        assert norm_value >= 0
        return norm_value

    class _CoveredEmbeddings:
        def __init__(self, covered_embed_cutoff):
            self.covered_embeddings = set()
            self._covered_embed_cutoff = covered_embed_cutoff

        def add(self, dim):
            self.covered_embeddings.add(dim)
            if len(self.covered_embeddings) >= self._covered_embed_cutoff:
                return True
            else:
                return False

    def search(
        self, embed_vector: np.array, approx_max_result_count=DEFAULT_MAX_RESULT_COUNT
    ) -> List[str]:
        assert embed_vector.shape[0] == self._embedding_vector_len
        for embed_idx in range(self._embedding_vector_len):
            embed_vector[embed_idx] = self._normalize_embed_value(
                embed_vector[embed_idx]
            )

        found_embedding_cutoff = int(
            COVERED_EMBED_CUTOFF_PROP * self._embedding_vector_len
        )
        search = {}
        results = []
        for abs_delta in range(SEARCH_DISTANCE):
            if abs_delta > 0:
                delta_options = [abs_delta, -abs_delta]
            else:
                delta_options = [abs_delta]
            for delta in delta_options:
                for embed_idx in range(self._embedding_vector_len):
                    next_embed = min(embed_vector[embed_idx] + delta, self._max_index)
                    next_embed = max(next_embed, 0)
                    included_doc_idxs = self._index[embed_idx, int(next_embed)]
                    for doc_idx in included_doc_idxs:
                        if doc_idx not in search:
                            search[doc_idx] = self._CoveredEmbeddings(found_embedding_cutoff)
                        if search[doc_idx].add(next_embed):
                            results.append(self._corpus[doc_idx])
                    if len(results) >= approx_max_result_count:
                        return results
        return results

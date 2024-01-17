from nlp.vector_search import BaseVectorSearch

from typing import Final, Tuple, List
import numpy as np


NORM_RANGE: Final[Tuple[int, int]] = (-100, 100)
DEFAULT_MAX_RESULT_COUNT: Final[int] = 5
SEARCH_DISTANCE: Final[int] = 10
COVERED_DIM_CUTOFF_PROP: Final[float] = 0.7


class PerpendicularSearch(BaseVectorSearch):
    def __init__(
        self,
        corpus_vectors: List[np.array],
    ):
        self._vector_len = len(corpus_vectors[0])

        self._search_range = NORM_RANGE[1] - NORM_RANGE[0] + 1
        self._max_index = self._search_range - 1

        self._index = np.empty((self._vector_len, self._search_range), dtype=object)
        for r in range(self._index.shape[0]):
            for c in range(self._index.shape[1]):
                self._index[r, c] = []

        self._corpus_vectors = corpus_vectors
        for corpus_idx in range(len(corpus_vectors)):
            corpus_vector = self._corpus_vectors[corpus_idx]
            for dim in range(self._vector_len):
                norm_vector_value = self._normalize_vector_value(corpus_vector[dim])
                self._index[dim, norm_vector_value].append(corpus_idx)

    def _normalize_vector_value(self, vector_value: float) -> int:
        norm_value = int(vector_value * NORM_RANGE[1]) + NORM_RANGE[1]
        assert norm_value >= 0
        return norm_value

    class _VectorDimCoverage:
        def __init__(self, vector_coverage_cutoff):
            self._covered_dims = set()
            self._vector_coverage_cutoff = vector_coverage_cutoff
            self._added = False

        def add(self, dim):
            if self._added:
                return False
            self._covered_dims.add(dim)
            if len(self._covered_dims) >= self._vector_coverage_cutoff:
                self._added = True
                return True
            else:
                return False

    def search(
        self, vector: np.array, approx_max_result_count=DEFAULT_MAX_RESULT_COUNT
    ) -> List[int]:
        assert vector.shape[0] == self._vector_len
        vector_copy = np.copy(vector)
        for dim in range(self._vector_len):
            vector_copy[dim] = self._normalize_vector_value(vector_copy[dim])

        dim_coverage_cutoff = int(COVERED_DIM_CUTOFF_PROP * self._vector_len)
        search = {}
        results = []
        for abs_delta in range(SEARCH_DISTANCE):
            if abs_delta > 0:
                delta_options = [abs_delta, -abs_delta]
            else:
                delta_options = [abs_delta]
            for delta in delta_options:
                for dim in range(self._vector_len):
                    next_value = min(vector_copy[dim] + delta, self._max_index)
                    next_value = max(next_value, 0)
                    included_doc_idxs = self._index[dim, int(next_value)]
                    for doc_idx in included_doc_idxs:
                        if doc_idx not in search:
                            search[doc_idx] = self._VectorDimCoverage(
                                dim_coverage_cutoff
                            )
                        if search[doc_idx].add(dim):
                            results.append(doc_idx)
                    if len(results) >= approx_max_result_count:
                        return results
        return results

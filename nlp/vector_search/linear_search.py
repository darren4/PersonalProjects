from nlp.vector_search import BaseVectorSearch

import numpy as np
from typing import List


class LinearVectorSearch(BaseVectorSearch):
    def __init__(
        self,
        corpus_vectors: List[np.array],
    ):
        self._corpus_vectors = corpus_vectors

    def _calculate_cos_similarity(self, lhs: np.array, rhs: np.array) -> float:
        lhs, rhs = lhs.flatten(), rhs.flatten()
        return np.dot(lhs, rhs) / (np.linalg.norm(lhs) * np.linalg.norm(rhs))

    def search(self, vector: np.array, approx_max_result_count=5):
        results = []
        for corpus_idx in range(len(self._corpus_vectors)):
            corpus_vector = self._corpus_vectors[corpus_idx]
            similarity = self._calculate_cos_similarity(vector, corpus_vector)
            if len(results) == approx_max_result_count:
                if similarity > results[-1][0]:
                    results[-1] = (similarity, corpus_idx)
            else:
                results.append((similarity, corpus_idx))
            results.sort(reverse=True)
        final_results = []
        for result in results:
            final_results.append(result[1])
        return final_results

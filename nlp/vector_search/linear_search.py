from nlp.vector_search import BaseVectorSearch

import numpy as np
from typing import Tuple, List


class LinearVectorSearch(BaseVectorSearch):
    def __init__(
        self,
        corpus_vectors: List[np.array],
    ):
        self._corpus_vectors = corpus_vectors

    def search(self, vector: np.array, approx_max_result_count=5):
        results = []
        for corpus_idx in range(len(self._corpus_vectors)):
            corpus_vector = self._corpus_vectors[corpus_idx]
            dist = np.linalg.norm(abs(vector - corpus_vector))

            if len(results) == approx_max_result_count:
                if dist < results[-1][0]:
                    results[-1] = (dist, corpus_idx)
            else:
                results.append((dist, corpus_idx))
            results.sort()
        final_results = []
        for result in results:
            final_results.append(result[1])
        return final_results

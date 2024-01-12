from nlp.vector_search import BaseVectorSearch

import numpy as np
from typing import Tuple, List


class LinearVectorSearch(BaseVectorSearch):
    def __init__(
        self,
        corpus: List[str],
        embeddings: List[np.array],
    ):
        self.corpus = corpus
        self._corpus_embeddings: List[Tuple(str, np.array)] = []
        for i in range(len(corpus)):
            self._corpus_embeddings.append((corpus[i], embeddings[i]))

    def search(self, vector: np.array, approx_max_result_count=5):
        results = []
        for corpus_idx in range(len(self._corpus_embeddings)):
            word_embedding = self._corpus_embeddings[corpus_idx]
            dist = np.linalg.norm(abs(vector - word_embedding[1]))

            if len(results) == approx_max_result_count:
                if dist < results[-1][0]:
                    results[-1] = (dist, word_embedding)
            else:
                results.append((dist, corpus_idx))
            results.sort()
        final_results = []
        for result in results:
            final_results.append(result[1])
        return final_results

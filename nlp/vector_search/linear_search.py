from nlp.vector_search import BaseVectorSearch

from torch import tensor
from torch.nn import CosineSimilarity
from typing import List


class LinearVectorSearch(BaseVectorSearch):
    def __init__(
        self,
        corpus_vectors: List[tensor],
    ):
        self._corpus_vectors = corpus_vectors
        self._cos = CosineSimilarity(dim=0)

    def search(self, vector: tensor, approx_max_result_count=5):
        results = []
        for corpus_idx in range(len(self._corpus_vectors)):
            corpus_vector = self._corpus_vectors[corpus_idx]
            similarity = self._cos(vector, corpus_vector)

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

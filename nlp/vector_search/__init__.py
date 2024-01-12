import numpy as np
from abc import ABC, abstractmethod
from typing import List


class SearchResult:
    def __init__(self, corpus_idx, sentence, vector):
        self.corpus_idx = corpus_idx
        self.sentence = sentence
        self.vector = vector

class BaseVectorSearch(ABC):
    @abstractmethod
    def __init__(
        self,
        corpus: List[str],
        embeddings: List[np.array],
    ):
        raise NotImplementedError()

    @abstractmethod
    def search(
        self, embed_vector: np.array, approx_max_result_count
    ) -> List[SearchResult]:
        raise NotImplementedError()

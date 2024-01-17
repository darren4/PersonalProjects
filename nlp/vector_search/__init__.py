import numpy as np
from abc import ABC, abstractmethod
from typing import List


class BaseVectorSearch(ABC):
    @abstractmethod
    def __init__(
        self,
        corpus_vectors: List[np.array],
    ):
        raise NotImplementedError()

    @abstractmethod
    def search(self, vector: np.array, approx_max_result_count) -> List[int]:
        raise NotImplementedError()

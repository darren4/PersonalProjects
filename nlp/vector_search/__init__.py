import numpy as np
from abc import ABC, abstractmethod
from typing import Final, Tuple, List


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
    ) -> List[Tuple[str, np.array]]:
        raise NotImplementedError()

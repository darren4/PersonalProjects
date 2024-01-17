from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseVectorize(ABC):
    @abstractmethod
    def vectorize(self, strings: List[str]) -> List[np.array]:
        pass

    
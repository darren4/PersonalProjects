from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseVectorize(ABC):
    @abstractmethod
    def vectorize(self, strings: List[str]) -> List[np.array]:
        pass

    def last_unknown_prop(self):
        return 0.0

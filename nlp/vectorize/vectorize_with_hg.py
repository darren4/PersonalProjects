from nlp.vectorize.base_vectorize import BaseVectorize

from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class VectorizeWithHG(BaseVectorize):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self._model = SentenceTransformer(model_name)

    def vectorize(self, strings: List[str]) -> List[np.array]:
        return self._model.encode(strings, convert_to_numpy=True)

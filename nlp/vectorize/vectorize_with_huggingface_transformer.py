from nlp.vectorize.base_vectorize import BaseVectorize

from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np
import torch


class VectorizeWithHG(BaseVectorize):
    def __init__(self, model_name="sentence-t5-base"):
        self._model: SentenceTransformer = SentenceTransformer(model_name)

    def vectorize(
        self, strings: List[str], convert_to_tensor=False
    ) -> List[Union[np.array, torch.Tensor]]:
        return self._model.encode(strings, convert_to_tensor=convert_to_tensor)

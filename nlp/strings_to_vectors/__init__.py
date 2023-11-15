import typing
from typing import List
from abc import ABC, abstractmethod
import torch



class StringsToVectors(ABC):
    def __init__(self, source: typing.Union[str, list], write_path: str=None):
        pass
    
    @abstractmethod
    def to_vectors(self, strings: List[str]) -> torch.tensor:
        raise NotImplementedError()
    

class GloveWordEmbedding (StringsToVectors):
    def __init__(self, source: typing.Union[str, List[str]], write_path: str=None):
        if type(source) == str:
            pass
        elif type(source) == list:
            pass
        else:
            raise ValueError("source must be filepath or list of strings")
    
    def to_vectors(self, strings: List[str]) -> torch.tensor:
        raise NotImplementedError()

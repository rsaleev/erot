from abc import ABC, abstractmethod


class BaseTransformer(ABC):


    @classmethod
    @abstractmethod
    def transform(cls, *args, **kwargs):
        raise NotImplementedError
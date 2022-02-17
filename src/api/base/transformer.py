from abc import ABC, abstractmethod, abstractproperty


class BaseTransformer(ABC):

    @abstractmethod
    def transform(self, *args, **kwargs):
        raise NotImplementedError
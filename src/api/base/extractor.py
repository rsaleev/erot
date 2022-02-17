from abc import ABC, abstractmethod

class BaseExtractor(ABC):

    @abstractmethod
    def extract(self, *args, **kwargs):
        raise NotImplementedError


class DocumentExtractor(BaseExtractor):

    @abstractmethod
    def read(self, *args, **kwargs):
        raise NotImplementedError
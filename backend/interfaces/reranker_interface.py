from abc import ABC, abstractmethod


class RerankerInterface(ABC):

    @abstractmethod
    def health(self):
        pass

    @abstractmethod
    def rerank(self, query, documents, top_n):
        pass

from abc import ABC, abstractmethod


class VectorDBInterface(ABC):
    
    @abstractmethod
    def health(self):
        pass

    @abstractmethod
    def upsert(self, documents):
        pass

    @abstractmethod
    def filter_search(self, filters):
        pass   
    
    @abstractmethod
    def filter_delete(self, filters):
        pass
    
    @abstractmethod
    def semantic_search(self, query_vector, top_k):
        pass
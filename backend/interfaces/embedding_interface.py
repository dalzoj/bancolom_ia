from abc import ABC, abstractmethod

class EmbeddingInterface(ABC):
    
    @abstractmethod
    def health(self):
        pass

    @abstractmethod
    def embed_batch(self, data):
        pass
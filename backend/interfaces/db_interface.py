from abc import ABC, abstractmethod

class DBInterface(ABC):

    @abstractmethod
    def _connect(self):
        pass
    
    @abstractmethod
    def execute_query(self):
        pass
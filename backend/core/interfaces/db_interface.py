from abc import ABC, abstractmethod

class DBInterface(ABC):

    @abstractmethod
    def _connect():
        pass
    
    @abstractmethod
    def execute_query():
        pass
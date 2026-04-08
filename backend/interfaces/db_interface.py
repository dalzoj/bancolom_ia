from abc import ABC, abstractmethod


class DBInterface(ABC):

    @abstractmethod
    def execute_query(self, query, values=()):
        pass

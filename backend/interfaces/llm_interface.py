from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    def health(self):
        pass

    @abstractmethod
    def generate(self, messages, system):
        pass
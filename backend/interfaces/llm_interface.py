from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    def health(self):
        pass

    @abstractmethod
    def generate(self, system_prompt, user_prompt):
        pass

    @abstractmethod
    def first_step_generate(self, system_prompt, messages, tools):
        pass

    @abstractmethod
    def final_step_generate(self, system_prompt, messages, tools):
        pass

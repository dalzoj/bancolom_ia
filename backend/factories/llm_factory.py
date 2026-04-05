from backend.core.config_loader import config


class LLMFactory:

    @staticmethod
    def create():

        provider = config.llm_provider

        if provider == "cohere":
            from backend.providers.llm.cohere_handler import CohereHandler
            return CohereHandler()

        raise ValueError(f"Proveedor de LLM '{provider}' no está soportado.")
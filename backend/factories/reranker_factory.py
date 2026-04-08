from backend.core.config_loader import config


class RerankerFactory:

    @staticmethod
    def create():
        provider = config.reranking_provider

        if provider == "cohere":
            from backend.providers.reranker.cohere_reranker_handler import CohereRerankerHandler
            return CohereRerankerHandler()

        raise ValueError(f"Proveedor de Reranker '{provider}' no está soportado.")

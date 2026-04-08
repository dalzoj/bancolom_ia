from backend.core.config_loader import config


class EmbeddingFactory:
    @staticmethod
    def create():

        provider = config.embedding_provider

        if provider == "cohere":
            from backend.providers.embedding.cohere_handler import CohereHandler

            return CohereHandler()

        raise ValueError(f"Provedor de Embedding '{provider}' no está soportado.")

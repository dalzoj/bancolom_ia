from backend.core.config_loader import config


class VectorDBFactory:

    @staticmethod
    def create():
        
        provider = config.vector_db_provider

        if provider == "pinecone":
            from backend.providers.vector_db.pinecone_handler import PineconeHandler
            return PineconeHandler()
        
        raise ValueError(f"Provedor de Vector DB '{provider}' no está soportado.")
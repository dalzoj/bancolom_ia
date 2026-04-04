from cohere import Client

from backend.interfaces.embedding_interface import EmbeddingInterface
from backend.core.config_loader import config

class CohereHandler(EmbeddingInterface):
    
    def __init__(self):
        self._client = Client(api_key=config.env("COHERE_API_KEY"))
        self._model = config.embedding_model
        self._dimension = config.embedding_dimension
        
    def health(self):
        try:
            self._client.models.list()
            print("INFO: Cohere conectado correctamente.")
            return True
        except Exception as e:
            print(f"ERROR: Cohere no disponible — {e}")
            return False

    def embed_batch(self, data):
        try:
            response = self._client.embed(
                texts = data,
                model = self._model,
                input_type = "search_document",
                embedding_types = ["float"]
            )
            return response.embeddings.float
        except Exception as e:
            print(f"ERROR: No se pudo generar el batch de embeddings — {e}")
            return []
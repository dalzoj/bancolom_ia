from backend.factories.embedding_factory import EmbeddingFactory
from backend.factories.vector_db_factory import VectorDBFactory
from backend.core.config_loader import config


class Retrieve:

    def __init__(self):
        self._embedder = EmbeddingFactory.create()
        self._vector_db = VectorDBFactory.create()
        self._top_k = config.vector_db_top_k
        
        if not self._embedder.health() or not self._vector_db.health():
            raise RuntimeError("ERROR: No se puede continuar, uno o más servicios no están disponibles.")

    def retrieve(self, query):        
        query = query.strip()
        query_embedding = self._embedder.embed_query(query)
        results = self._vector_db.semantic_search(query_embedding, self._top_k)

        print(f"INFO: Se han recuperado {len(results)} elementos.")
        return results
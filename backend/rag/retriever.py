from backend.factories.embedding_factory import EmbeddingFactory
from backend.factories.vector_db_factory import VectorDBFactory
from backend.core.models import SearchResult
from backend.core.config_loader import config


class Retriever:

    def __init__(self):
        self._embedder = EmbeddingFactory.create()
        self._vector_db = VectorDBFactory.create()
        self._top_k = config.vector_db_top_k
        
        if not self._embedder.health() or not self._vector_db.health():
            raise RuntimeError("ERROR: No se puede continuar, uno o más servicios no están disponibles.")

    def retriever(self, query):
        print(f'INFO: Iniciando recuperación.')
        
        query = query.strip()
        
        query_embedding = self._embedder.embed_query(query)
        
        raw_results = self._vector_db.semantic_search(query_embedding, self._top_k)
        
        results = [
            SearchResult(
                url = r["url"],
                title = r["title"],
                chunk_text = r["chunk_text"],
                chunk_index = r["chunk_index"],
                extracted_date = r["extracted_date"],
                score = r["score"]
            )
            for r in raw_results
        ]

        print(f"INFO: Se han recuperado {len(results)} elementos.")
        return results
import sys

from backend.factories.embedding_factory import EmbeddingFactory
from backend.factories.vector_db_factory import VectorDBFactory
from backend.factories.reranker_factory import RerankerFactory
from backend.core.config_loader import config


class Retriever:

    def __init__(self):
        self._embedder = EmbeddingFactory.create()
        self._vector_db = VectorDBFactory.create()
        self._top_k = config.vector_db_top_k

        self._reranking_enabled = config.reranking_enabled
        self._reranker = RerankerFactory.create() if self._reranking_enabled else None
        self._reranking_top_n = config.reranking_top_n

        if not self._embedder.health() or not self._vector_db.health():
            raise RuntimeError("ERROR: No se puede continuar, uno o más servicios no están disponibles.")

    def _rerank(self, query, results):
        print("INFO: Aplicando reranking.", file=sys.stderr)
        if not results or self._reranker is None:
            return results

        try:
            documents = [item["chunk_text"] for item in results]
            hits = self._reranker.rerank(query, documents, self._reranking_top_n)

            reranked = [
                {**results[hit["index"]], "score": hit["score"]}
                for hit in hits
            ]

            print(
                f"INFO: Reranking aplicado — {len(results)} candidatos → {len(reranked)} seleccionados.",
                file=sys.stderr,
            )
            return reranked

        except Exception as e:
            print(f"ERROR: Reranking falló, se retornan resultados originales — {e}", file=sys.stderr)
            return results[: self._reranking_top_n]

    def retrieve(self, query):
        print("INFO: Realizando recuperación de información", file=sys.stderr)
        query = query.strip()
        query_embedding = self._embedder.embed_query(query)

        results = self._vector_db.semantic_search(query_embedding, self._top_k)

        if self._reranking_enabled:
            results = self._rerank(query, results)

        return results

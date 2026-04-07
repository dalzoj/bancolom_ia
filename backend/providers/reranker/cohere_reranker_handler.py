import sys

from cohere import Client

from backend.interfaces.reranker_interface import RerankerInterface
from backend.core.config_loader import config


class CohereRerankerHandler(RerankerInterface):

    def __init__(self):
        self._client = Client(api_key=config.env("COHERE_API_KEY"))
        self._model = config.reranking_model

    def health(self):
        try:
            self._client.models.list()
            print("INFO: Cohere Reranker conectado correctamente.", file=sys.stderr)
            return True
        except Exception as e:
            print(f"ERROR: Cohere Reranker no disponible — {e}", file=sys.stderr)
            return False

    def rerank(self, query, documents, top_n):
        response = self._client.rerank(
            model=self._model,
            query=query,
            documents=documents,
            top_n=top_n,
        )
        return [
            {"index": hit.index, "score": round(hit.relevance_score, 4)}
            for hit in response.results
        ]
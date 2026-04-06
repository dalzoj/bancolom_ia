from pinecone import Pinecone, ServerlessSpec

from backend.interfaces.vector_db_interface import VectorDBInterface
from backend.core.config_loader import config

_PINECONE_CLOUD = "aws"
_PINECONE_REGION = "us-east-1"
_UPSERT_BATCH_SIZE = 100


class PineconeHandler(VectorDBInterface):
    
    def __init__(self):
        self._client = Pinecone(api_key=config.env("PINECONE_API_KEY"))
        self._index_name = config.vector_db_index
        self._dimension = config.vector_db_dimension
        self._metric = config.vector_db_metric
        self._top_k = config.vector_db_top_k
        self._check_index()
        
    def _check_index(self):
        existing = [i.name for i in self._client.list_indexes().indexes]
        if self._index_name not in existing:
            self._client.create_index(
                name = self._index_name,
                dimension = self._dimension,
                metric = self._metric,
                spec = ServerlessSpec(cloud=_PINECONE_CLOUD, region=_PINECONE_REGION)
            )
            print(f"INFO: Índice '{self._index_name}' creado con dimensión {self._dimension}.")
        else:
            print(f"INFO: Índice '{self._index_name}' encontrado.")
            
    def _get_index_client(self):
        return self._client.Index(self._index_name)
            
    @staticmethod
    def to_pinecone_format(vector):
        return {
            "id": vector.id,
            "values": vector.values,
            "metadata": {
                "url": vector.url,
                "title": vector.title,
                "extracted_date": vector.extracted_date,
                "chunk_index": vector.chunk_index,
                "chunk_text": vector.chunk_text,
                "category": vector.category,
            },
        }
        
    def health(self):
        try:
            self._client.list_indexes()
            print("INFO: Pinecone conectado correctamente.")
            return True
        except Exception as e:
            print(f"ERROR: Pinecone no disponible — {e}")
            return False
    
    def upsert(self, vectors):        
        try:
            index = self._get_index_client()
            total_batches = -(-len(vectors) // _UPSERT_BATCH_SIZE)

            for batch_num, start in enumerate(range(0, len(vectors), _UPSERT_BATCH_SIZE), start=1):
                batch = [self.to_pinecone_format(v) for v in vectors[start:start + _UPSERT_BATCH_SIZE]]
                index.upsert(vectors=batch)
                print(f"INFO: Insertado lote {batch_num} de {total_batches}")

            print(f"INFO: {len(vectors)} vectores insertados correctamente.")
        except Exception as e:
            print(f"ERROR: No se pudo realizar el upsert — {e}")   

    def filter_search(self, filters):
        try:
            results = self._get_index_client().query(
                vector=[0.0] * self._dimension,
                top_k=1,
                filter=filters,
                include_metadata=False,
            )
            return len(results["matches"]) > 0
        except Exception as e:
            print(f"ERROR: No se pudo buscar — {e}")
            return False

    def filter_delete(self, filters):
        try:
            self._get_index_client().delete(filter=filters)
            print(f"INFO: Vectores eliminados con filtros {filters}")
        except Exception as e:
            print(f"ERROR: No se pudo eliminar — {e}")
            
    def semantic_search(self, query_vector, top_k):
        try:
            results = self._get_index_client().query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
            )

            return [
                {
                    "url": match["metadata"].get("url", ""),
                    "title": match["metadata"].get("title", ""),
                    "chunk_text": match["metadata"].get("chunk_text", ""),
                    "chunk_index": match["metadata"].get("chunk_index", 0),
                    "extracted_date": match["metadata"].get("extracted_date", ""),
                    "category": match["metadata"].get("category", "general"),
                    "score": round(match["score"], 4)
                }
                for match in results["matches"]
            ]
        except Exception as e:
            print(f"ERROR: No se pudo realizar la búsqueda semántica — {e}")
            return []
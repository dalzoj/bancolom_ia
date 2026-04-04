from pinecone import Pinecone, ServerlessSpec

from backend.interfaces.vector_db_interface import VectorDBInterface
from backend.core.config_loader import config

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
                spec = ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"INFO: Índice '{self._index_name}' creado con dimensión {self._dimension}.")
        else:
            print(f"INFO: Índice '{self._index_name}' encontrado.")
        
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
            index = self._client.Index(self._index_name)
            
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = [v.to_pinecone_format() for v in vectors[i:i + batch_size]]
                index.upsert(vectors=batch)
                print(f"INFO: Insertado lote {i // batch_size + 1} de {-(-len(vectors) // batch_size)}")
            
            print(f"INFO: {len(vectors)} vectores insertados correctamente.")
        except Exception as e:
            print(f"ERROR: No se pudo realizar el upsert — {e}")

    def filter_search(self, filters):
        try:
            index = self._client.Index(self._index_name)
            results = index.query(
                vector = [0.0] * self._dimension,
                top_k = 1,
                filter = filters,
                include_metadata = False
            )
            return len(results["matches"]) > 0
        except Exception as e:
            print(f"ERROR: No se pudo buscar — {e}")
            return False

    def filter_delete(self, filters):
        try:
            index = self._client.Index(self._index_name)
            index.delete(filter=filters)
            print(f"INFO: Vectores eliminados con filtros {filters}")
        except Exception as e:
            print(f"ERROR: No se pudo eliminar — {e}")
import sys

from backend.factories.embedding_factory import EmbeddingFactory
from backend.factories.vector_db_factory import VectorDBFactory
from backend.core.models import ChunkData, VectorData

_CHUNK_SIZE = 400
_CHUNK_OVERLAP = 50


class Indexer:

    def __init__(self):
        self._embedder = EmbeddingFactory.create()
        self._vector_db = VectorDBFactory.create()
        if not self._embedder.health() or not self._vector_db.health():
            raise RuntimeError("ERROR: No se puede continuar, uno o más servicios no están disponibles.")
        
    def _generate_chunks_data(self, data, chunk_size = _CHUNK_SIZE, overlap = _CHUNK_OVERLAP):
        chunks = []
        
        for page in data:
            words = page.clean_text.split()
            start=0
            chunk_index=0
            
            while start < len(words):
                chunk_text = " ".join(words[start:start + chunk_size])
                chunks.append(ChunkData(
                    url=page.url,
                    title=page.title,
                    extracted_date=page.extracted_date,
                    chunk_index=chunk_index,
                    chunk_text=chunk_text,
                    category=page.category,
                ))
                
                start += chunk_size - overlap
                chunk_index += 1
        
        print(f"INFO: Se generaron {len(chunks)} chunks de {len(data)} elementos.", file=sys.stderr)
        return chunks
    
    def _index(self, chunks_data):
        
        # Agrupar chunks por URL
        chunks_by_url = {}
        for chunk in chunks_data:
            chunks_by_url.setdefault(chunk.url, []).append(chunk)

        # Recorrer agrupación por URL
        for url, chunks in chunks_by_url.items():
            try:
                if self._vector_db.filter_search({"url": url}):
                    self._vector_db.filter_delete({"url": url})
                    print(f"INFO: URL existente, reemplazando {url}", file=sys.stderr)

                texts = [chunk.chunk_text for chunk in chunks]
                embeddings = self._embedder.embed_batch(texts)

                vectors = [
                    VectorData(
                        id=f"{chunk.url}-chunk_{chunk.chunk_index}",
                        values=embedding,
                        url=chunk.url,
                        title=chunk.title,
                        extracted_date=chunk.extracted_date,
                        chunk_index=chunk.chunk_index,
                        chunk_text=chunk.chunk_text,
                        category=chunk.category,
                    )
                    for chunk, embedding in zip(chunks, embeddings)
                ]

                self._vector_db.upsert(vectors)
                print(f"INFO: Indexados {len(vectors)} chunks para {url}", file=sys.stderr)

            except Exception as e:
                print(f"ERROR: Falló la indexación de {url}, continuando con el siguiente. Detalle: {e}", file=sys.stderr)
                continue
    
    def index_data(self, data):
        print(f"INFO: Indexación de datos.", file=sys.stderr)
        
        chunk_data = self._generate_chunks_data(data)
        self._index(chunk_data)
from backend.rag.retriever import Retrieve


_retriever = None

def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retrieve()
    return _retriever


def search_knowledge_base(query, top_k):

    query = query.strip()
    if not query:
        return {"error": "La consulta no puede estar vacía.", "results": []}

    try:
        retriever = _get_retriever()
        
        if top_k is not None:
            results = retriever._vector_db.semantic_search(
                retriever._embedder.embed_query(query), top_k
            )
        else:
            results = retriever.retrieve(query)

        if not results:
            return {
                "message": "No se encontraron documentos relevantes para la consulta.",
                "results": []
            }

        return {
            "total": len(results),
            "results": [
                {
                    "url": item["url"],
                    "title": item["title"],
                    "category": item["category"],
                    "score": item["score"],
                    "chunk_text": item["chunk_text"],
                    "chunk_index": item["chunk_index"],
                    "extracted_date": item["extracted_date"],
                }
                for item in results
            ]
        }

    except RuntimeError as e:
        return {"error": f"Servicio no disponible: {str(e)}", "results": []}
    except Exception as e:
        return {"error": f"Error inesperado al buscar: {str(e)}", "results": []}
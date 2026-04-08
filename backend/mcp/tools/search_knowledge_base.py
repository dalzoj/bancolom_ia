import sys
import threading

from backend.rag.retriever import Retriever

_retriever = None
_retriever_lock = threading.Lock()


def _get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        with _retriever_lock:
            if _retriever is None:
                _retriever = Retriever()
    return _retriever


def search_knowledge_base(query: str) -> dict:
    """
    Ejecuta una búsqueda semántica en la base de conocimiento vectorial
    y retorna los documentos más relevantes con metadatos.

    Args:
        query: Consulta en lenguaje natural. No puede estar vacía.
        top_k: Número de resultados a retornar. Debe ser un entero
               entre 1 y 10. Por defecto 5.

    Returns:
        Diccionario con 'total' y 'results'. Cada resultado incluye url,
        title, category, score, chunk_text, chunk_index y extracted_date.
        En caso de error retorna un diccionario con clave 'error'.
    """
    print(
        "INFO: Ejecutando búsqueda semántica (search_knowledge_base).", file=sys.stderr
    )

    if not isinstance(query, str):
        return {
            "error": "El parámetro 'query' debe ser una cadena de texto.",
            "results": [],
        }

    query = query.strip()
    if not query:
        return {"error": "La consulta no puede estar vacía.", "results": []}

    try:
        retriever = _get_retriever()
        results = retriever.retrieve(query)

        if not results:
            return {
                "message": "No se encontraron documentos relevantes para la consulta.",
                "results": [],
            }

        print(
            f"INFO: Se ha retornado {len(results)} registros de información.",
            file=sys.stderr,
        )

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
            ],
        }

    except RuntimeError as e:
        return {"error": f"Servicio no disponible: {str(e)}", "results": []}

    except TimeoutError as e:
        return {
            "error": f"Tiempo de espera agotado al consultar la base vectorial: {str(e)}",
            "results": [],
        }

    except Exception as e:
        return {"error": f"Error inesperado al buscar: {str(e)}", "results": []}

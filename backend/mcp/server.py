import sys
import json
from datetime import datetime, timezone

from fastmcp import FastMCP

from backend.core.config_loader import config
from backend.factories.db_factory import DBFactory
from backend.mcp.tools.search_knowledge_base import search_knowledge_base as _search_knowledge_base
from backend.mcp.tools.get_article_by_url import get_article_by_url as _get_article_by_url
from backend.mcp.tools.list_categories import list_categories as _list_categories


mcp = FastMCP(name="bancolombia-knowledge-base")

@mcp.tool()
def search_knowledge_base_tool(query: str) -> str:
    """
    Tool que busca documentos relevantes en la base de conocimiento
    usando búsqueda semántica.

    Se usa cuando el usuario haga preguntas sobre productos, servicios,
    condiciones, requisitos o cualquier información publicada en el sitio
    web de Bancolombia para personas.

    Retorna los fragmentos más relevantes junto con su URL de origen,
    categoría y score de relevancia.

    Args:
        query: Pregunta o consulta en lenguaje natural del usuario.
               Debe ser descriptiva para maximizar la precisión semántica.
               Ejemplo: '¿Cuáles son los requisitos para un crédito de vivienda?'

    Returns:
        JSON con 'total' y lista de 'results', donde cada resultado incluye: url, title, category,
        score (0-1), chunk_text, chunk_index y extracted_date.
        En caso de error retorna un campo 'error'.
    """

    result = _search_knowledge_base(query)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_article_by_url_tool(url: str) -> str:
    """
    Tool que recupera el contenido completo de un artículo indexado a partir de su URL.

    Se usa cuando el usuario solicite información detallada de una página
    específica de Bancolombia, cuando quiera leer un artículo completo,
    o cuando necesites ampliar la información de un resultado obtenido
    con search_knowledge_base_tool.

    La URL debe pertenecer al dominio www.bancolombia.com/personas.

    Args:
        url: URL exacta de la página de Bancolombia indexada en la base de
             conocimiento.
             Ejemplo: 'https://www.bancolombia.com/personas/creditos/vivienda'

    Returns:
        JSON con los campos: url, title, category, extracted_date y clean_text con el contenido completo del artículo.
        En caso de no encontrarlo retorna un campo 'error'.
    """

    result = _get_article_by_url(url)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def list_categories_tool() -> str:
    """
    Tool que lista todas las categorías de contenido disponibles en la base de conocimiento,
    junto con el número de artículos por categoría.

    Se usa cuando el usuario pregunte qué temas o secciones cubre el asistente,
    cuando necesites orientar al usuario sobre qué información está disponible,
    o cuando quieras filtrar una búsqueda posterior por categoría relevante.

    No recibe parámetros.

    Returns:
        JSON con 'total_categories' y lista de 'categories', donde cada elemento
        incluye 'category' (nombre de la categoría) y 'total_articles' (cantidad de artículos indexados en esa categoría).
        En caso de error retorna un campo 'error'.
    """

    result = _list_categories()
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.resource("knowledgebase://stats")
def knowledgebase_stats():
    """
    Resource que expone las estadísticas actuales de la base de conocimiento.

    Se usa cuando el cliente necesite conocer el estado general del sistema:
    total de documentos indexados, categorías disponibles, fecha de última
    actualización y configuración del modelo de embeddings utilizado.

    URI: knowledgebase://stats

    Returns:
        JSON con los campos:
        - total_documents (int): número total de artículos indexados.
        - total_categories (int): número de categorías distintas.
        - categories (list[str]): nombres de las categorías disponibles.
        - last_updated (str | None): fecha ISO 8601 de la extracción más reciente.
        - embedding_model (str): nombre del modelo de embeddings configurado.
        - embedding_dimension (int): dimensionalidad del modelo de embeddings.
        - vector_db_provider (str): proveedor de base de datos vectorial en uso.
        - vector_db_index (str): nombre del índice vectorial activo.
        - generated_date (str): fecha ISO 8601 en que se generó esta respuesta.
        En caso de error retorna un campo 'error' con el detalle.
    """

    print("INFO: Ejecutando estadísticas de base de conocimiento (knowledgebase_stats).", file=sys.stderr)
    try:
        db = DBFactory.create()

        total_docs = db.execute_query(
            f"SELECT COUNT(*) AS total FROM {config.sql_lite_data_table}"
        )
        total = total_docs[0]["total"] if total_docs else 0

        categories = db.execute_query(
            f"SELECT DISTINCT category FROM {config.sql_lite_data_table}"
        )
        category_list = [row["category"] for row in categories]

        last_updated = db.execute_query(
            f"""
            SELECT MAX(extracted_date) AS last_date
            FROM {config.sql_lite_data_table}
            """
        )
        last_date = last_updated[0]["last_date"] if last_updated else None

        stats = {
            "total_documents": total,
            "total_categories": len(category_list),
            "categories": category_list,
            "last_updated": last_date,
            "embedding_model": config.embedding_model,
            "embedding_dimension": config.embedding_dimension,
            "vector_db_provider": config.vector_db_provider,
            "vector_db_index": config.vector_db_index,
            "generated_date": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(stats, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error al obtener estadísticas: {str(e)}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")

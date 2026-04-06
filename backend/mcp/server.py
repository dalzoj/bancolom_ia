import json
from datetime import datetime, timezone

from fastmcp import FastMCP

from backend.core.config_loader import config
from backend.factories.db_factory import DBFactory
from backend.mcp.tools.search_knowledge_base import search_knowledge_base
from backend.mcp.tools.get_article_by_url import get_article_by_url
from backend.mcp.tools.list_categories import list_categories


mcp = FastMCP(name="bancolombia-knowledge-base")

@mcp.tool()
def search_knowledge_base_tool(query, top_k):
    result = search_knowledge_base(query, top_k)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_article_by_url_tool(url):
    result = get_article_by_url(url)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def list_categories_tool():
    result = list_categories()
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.resource("knowledgebase://stats")
def knowledgebase_stats():
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
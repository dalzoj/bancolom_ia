from backend.factories.db_factory import DBFactory
from backend.core.config_loader import config


_db = None

def _get_db():
    global _db
    if _db is None:
        _db = DBFactory.create()
    return _db


def list_categories():
    try:
        db = _get_db()
        rows = db.execute_query(
            f"""
            SELECT category, COUNT(*) AS total
            FROM {config.sql_lite_data_table}
            GROUP BY category
            ORDER BY total DESC
            """
        )

        if not rows:
            return {
                "message": "La base de conocimiento aún no contiene artículos indexados.",
                "categories": []
            }

        return {
            "total_categories": len(rows),
            "categories": [
                {
                    "category": row["category"],
                    "total_articles": row["total"]
                }
                for row in rows
            ]
        }

    except Exception as e:
        return {"error": f"Error al listar categorías: {str(e)}"}
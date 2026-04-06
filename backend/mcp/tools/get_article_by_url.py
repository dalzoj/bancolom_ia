from backend.factories.db_factory import DBFactory
from backend.core.config_loader import config


_db = None

def _get_db():
    global _db
    if _db is None:
        _db = DBFactory.create()
    return _db


def get_article_by_url(url):

    url = url.strip()
    if not url:
        return {"error": "La URL no puede estar vacía."}

    try:
        db = _get_db()
        rows = db.execute_query(
            f"""
            SELECT url, title, extracted_date, clean_text, category
            FROM {config.sql_lite_data_table}
            WHERE url = ?
            LIMIT 1
            """,
            (url,)
        )

        if not rows:
            return {
                "error": f"No se encontró ningún artículo indexado con la URL: {url}"
            }

        row = rows[0]
        return {
            "url":            row["url"],
            "title":          row["title"],
            "category":       row["category"],
            "extracted_date": row["extracted_date"],
            "clean_text":     row["clean_text"],
        }

    except Exception as e:
        return {"error": f"Error al recuperar el artículo: {str(e)}"}
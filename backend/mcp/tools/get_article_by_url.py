import sys

import threading

from backend.factories.db_factory import DBFactory
from backend.core.config_loader import config
from backend.interfaces.db_interface import DBInterface

_ALLOWED_DOMAIN = "https://www.bancolombia.com/"

_db = None
_db_lock = threading.Lock()

def _get_db() -> DBInterface:
    global _db
    if _db is None:
        with _db_lock:
            if _db is None:
                _db = DBFactory.create()
    return _db

def get_article_by_url(url: str) -> dict:
    """
    Recupera el contenido completo de un artículo indexado buscándolo
    por su URL exacta en la base de datos relacional (SQLite).

    Args:
        url: URL exacta de una página de Bancolombia que haya sido
             indexada previamente. Debe comenzar con 'http' y pertenecer
             al dominio bancolombia.com.

    Returns:
        Diccionario con los campos: url, title, category, extracted_date
        y clean_text con el contenido completo del artículo.
        En caso de no encontrarlo o de error retorna un diccionario
        con clave 'error'.
    """
    print(f"INFO: Ejecutando búsqueda de contenido (get_article_by_url) en {url}.", file=sys.stderr)

    if not isinstance(url, str):
        return {"error": "El parámetro 'url' debe ser una cadena de texto."}

    url = url.strip()

    if not url:
        return {"error": "La URL no puede estar vacía."}

    if not url.startswith("http"):
        return {"error": "La URL debe comenzar con 'https://'."}

    if _ALLOWED_DOMAIN not in url:
        return {"error": f"La URL debe pertenecer al dominio '{_ALLOWED_DOMAIN}'."}

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
            return {"error": f"No se encontró ningún artículo indexado con la URL: {url}"}

        print(f"INFO: Se ha retornado {len(rows)} registros de información.", file=sys.stderr)

        row = rows[0]
        return {
            "url": row["url"],
            "title":  row["title"],
            "category": row["category"],
            "extracted_date": row["extracted_date"],
            "clean_text": row["clean_text"],
        }

    except TimeoutError as e:
        return {"error": f"Tiempo de espera agotado al consultar la base de datos: {str(e)}"}

    except Exception as e:
        return {"error": f"Error al recuperar el artículo: {str(e)}"}

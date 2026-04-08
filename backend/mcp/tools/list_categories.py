import sys

import threading

from backend.factories.db_factory import DBFactory
from backend.core.config_loader import config
from backend.interfaces.db_interface import DBInterface

_db = None
_db_lock = threading.Lock()

def _get_db() -> DBInterface:
    global _db
    if _db is None:
        with _db_lock:
            if _db is None:
                _db = DBFactory.create()
    return _db

def list_categories() -> dict:
    """
    Retorna todas las categorías de contenido disponibles en la base de
    conocimiento, junto con el conteo de artículos por categoría.

    Las categorías se derivan de la estructura de URLs del sitio
    www.bancolombia.com/personas (segundo segmento del path).
    No recibe parámetros.

    Returns:
        Diccionario con 'total_categories' (int) y 'categories' (lista
        de objetos con 'category' y 'total_articles').
        Si no hay artículos retorna un 'message' informativo.
        En caso de error retorna un diccionario con clave 'error'.
    """
    print("INFO: Ejecutando listado de categorias (list_categories).", file=sys.stderr)

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

        print(f"INFO: Se ha retornado {len(rows)} categorias.", file=sys.stderr)

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

    except TimeoutError as e:
        return {"error": f"Tiempo de espera agotado al consultar la base de datos: {str(e)}"}

    except Exception as e:
        return {"error": f"Error al listar categorías: {str(e)}"}

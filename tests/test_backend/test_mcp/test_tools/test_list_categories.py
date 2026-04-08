from unittest.mock import MagicMock, patch


CATEGORIAS_EJEMPLO = [
    {"category": "creditos", "total": 15},
    {"category": "ahorro",   "total": 8},
]


def _db_con(filas):
    db = MagicMock()
    db.execute_query.return_value = filas
    return db


def test_retorna_lista_de_categorias():
    with patch("backend.mcp.tools.list_categories._get_db", return_value=_db_con(CATEGORIAS_EJEMPLO)):
        from backend.mcp.tools.list_categories import list_categories
        result = list_categories()
    assert "categories" in result
    assert len(result["categories"]) == 2


def test_total_categories_coincide_con_filas():
    with patch("backend.mcp.tools.list_categories._get_db", return_value=_db_con(CATEGORIAS_EJEMPLO)):
        from backend.mcp.tools.list_categories import list_categories
        result = list_categories()
    assert result["total_categories"] == 2


def test_item_de_categoria_tiene_campos_correctos():
    with patch("backend.mcp.tools.list_categories._get_db", return_value=_db_con(CATEGORIAS_EJEMPLO)):
        from backend.mcp.tools.list_categories import list_categories
        result = list_categories()

    item = result["categories"][0]
    assert "category" in item
    assert "total_articles" in item


def test_db_vacia_retorna_mensaje_y_lista_vacia():
    with patch("backend.mcp.tools.list_categories._get_db", return_value=_db_con([])):
        from backend.mcp.tools.list_categories import list_categories
        result = list_categories()

    assert result["categories"] == []
    assert "message" in result


def test_excepcion_en_db_retorna_error():
    db = MagicMock()
    db.execute_query.side_effect = Exception("Conexión rechazada")

    with patch("backend.mcp.tools.list_categories._get_db", return_value=db):
        from backend.mcp.tools.list_categories import list_categories
        result = list_categories()

    assert "error" in result

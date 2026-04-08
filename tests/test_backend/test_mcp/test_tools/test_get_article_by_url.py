import pytest
from unittest.mock import MagicMock, patch


ARTICLE_ROW = {
    "url": "https://www.bancolombia.com/personas/creditos/vivienda",
    "title": "Crédito de Vivienda",
    "category": "creditos",
    "extracted_date": "2024-01-01",
    "clean_text": "Con el crédito de vivienda de Bancolombia puedes financiar tu hogar.",
}


def _fake_db(rows):
    db = MagicMock()
    db.execute_query.return_value = rows
    return db


def test_url_vacia_retorna_error():
    from backend.mcp.tools.get_article_by_url import get_article_by_url
    result = get_article_by_url("")
    assert "error" in result


def test_url_none_retorna_error():
    from backend.mcp.tools.get_article_by_url import get_article_by_url
    assert "error" in get_article_by_url(None)


def test_url_sin_protocolo_retorna_error():
    from backend.mcp.tools.get_article_by_url import get_article_by_url
    result = get_article_by_url("www.bancolombia.com/personas/creditos")
    assert "error" in result


def test_url_dominio_externo_retorna_error():
    from backend.mcp.tools.get_article_by_url import get_article_by_url
    result = get_article_by_url("https://www.nequi.com/personas/creditos")
    assert "error" in result


def test_url_no_encontrada_en_db_retorna_error():
    with patch("backend.mcp.tools.get_article_by_url._get_db", return_value=_fake_db([])):
        from backend.mcp.tools.get_article_by_url import get_article_by_url
        result = get_article_by_url("https://www.bancolombia.com/personas/pagina-inexistente")
    assert "error" in result


def test_url_valida_retorna_articulo_completo():
    with patch("backend.mcp.tools.get_article_by_url._get_db", return_value=_fake_db([ARTICLE_ROW])):
        from backend.mcp.tools.get_article_by_url import get_article_by_url
        result = get_article_by_url("https://www.bancolombia.com/personas/creditos/vivienda")

    assert result["url"] == ARTICLE_ROW["url"]
    assert result["title"] == ARTICLE_ROW["title"]
    assert "clean_text" in result


def test_resultado_tiene_todos_los_campos_requeridos():
    campos_esperados = ("url", "title", "category", "extracted_date", "clean_text")
    with patch("backend.mcp.tools.get_article_by_url._get_db", return_value=_fake_db([ARTICLE_ROW])):
        from backend.mcp.tools.get_article_by_url import get_article_by_url
        result = get_article_by_url("https://www.bancolombia.com/personas/creditos/vivienda")

    for campo in campos_esperados:
        assert campo in result, f"Falta el campo '{campo}' en la respuesta"

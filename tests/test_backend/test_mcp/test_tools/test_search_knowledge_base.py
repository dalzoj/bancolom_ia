from unittest.mock import MagicMock, patch


RESULTADO_EJEMPLO = [
    {
        "url": "https://www.bancolombia.com/personas/creditos/libre-inversion",
        "title": "Crédito de Libre Inversión",
        "category": "creditos",
        "score": 0.92,
        "chunk_text": "Con el crédito de libre inversión puedes financiar lo que necesitas.",
        "chunk_index": 0,
        "extracted_date": "2024-01-01",
    }
]


def _retriever_con(resultados):
    r = MagicMock()
    r.retrieve.return_value = resultados
    return r


def test_query_vacia_retorna_error():
    from backend.mcp.tools.search_knowledge_base import search_knowledge_base
    assert "error" in search_knowledge_base("")


def test_query_solo_espacios_retorna_error():
    from backend.mcp.tools.search_knowledge_base import search_knowledge_base
    assert "error" in search_knowledge_base("     ")


def test_query_no_string_retorna_error():
    from backend.mcp.tools.search_knowledge_base import search_knowledge_base
    assert "error" in search_knowledge_base(42)


def test_query_valida_retorna_resultados():
    with patch("backend.mcp.tools.search_knowledge_base._get_retriever",
               return_value=_retriever_con(RESULTADO_EJEMPLO)):
        from backend.mcp.tools.search_knowledge_base import search_knowledge_base
        result = search_knowledge_base("crédito de libre inversión")

    assert "results" in result
    assert result["total"] == 1
    assert result["results"][0]["url"] == RESULTADO_EJEMPLO[0]["url"]


def test_resultado_incluye_todos_los_campos():
    campos = ("url", "title", "category", "score", "chunk_text", "chunk_index", "extracted_date")
    with patch("backend.mcp.tools.search_knowledge_base._get_retriever",
               return_value=_retriever_con(RESULTADO_EJEMPLO)):
        from backend.mcp.tools.search_knowledge_base import search_knowledge_base
        result = search_knowledge_base("consulta cualquiera")

    item = result["results"][0]
    for campo in campos:
        assert campo in item, f"Falta '{campo}' en el resultado"


def test_sin_resultados_retorna_lista_vacia_y_mensaje():
    with patch("backend.mcp.tools.search_knowledge_base._get_retriever",
               return_value=_retriever_con([])):
        from backend.mcp.tools.search_knowledge_base import search_knowledge_base
        result = search_knowledge_base("algo que no existe en la base")

    assert result["results"] == []
    assert "message" in result


def test_error_en_retriever_retorna_clave_error():
    retriever = MagicMock()
    retriever.retrieve.side_effect = RuntimeError("Pinecone no responde")

    with patch("backend.mcp.tools.search_knowledge_base._get_retriever", return_value=retriever):
        from backend.mcp.tools.search_knowledge_base import search_knowledge_base
        result = search_knowledge_base("consulta válida")

    assert "error" in result

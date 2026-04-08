import pytest
from unittest.mock import patch

@pytest.fixture
def agent():
    with patch("backend.agent.ai_agent.LLMFactory") as mock_llm, \
         patch("backend.agent.ai_agent.DBFactory"), \
         patch("backend.agent.ai_agent.PromptLoader"), \
         patch("backend.agent.ai_agent.config") as mock_cfg:

        mock_cfg.mcp_server_path = "server.py"
        mock_cfg.sql_lite_conversation_table = "conversations"
        mock_cfg.sql_lite_summary_table = "summaries"
        mock_cfg.conversation_history_limit = 5
        mock_cfg.summary_every_turns = 5

        mock_llm.create.return_value.health.return_value = True

        from backend.agent.ai_agent import AIAgent
        return AIAgent()

def test_agent_raises_if_llm_unavailable():
    with patch("backend.agent.ai_agent.LLMFactory") as mock_llm_factory, \
         patch("backend.agent.ai_agent.DBFactory"), \
         patch("backend.agent.ai_agent.PromptLoader"), \
         patch("backend.agent.ai_agent.config") as mock_cfg:

        mock_cfg.mcp_server_path = "server.py"
        mock_llm_factory.create.return_value.health.return_value = False

        from backend.agent.ai_agent import AIAgent
        with pytest.raises(RuntimeError, match="LLM no está disponible"):
            AIAgent()


def test_format_context_lista_vacia(agent):
    assert agent._format_context([]) is None


def test_format_context_contiene_url_y_score(agent):
    items = [{"url": "https://bancolombia.com/creditos", "score": 0.85, "chunk_text": "Texto de prueba"}]
    result = agent._format_context(items)

    assert "https://bancolombia.com/creditos" in result
    assert "0.85" in result


def test_format_context_varias_fuentes_numeradas(agent):
    items = [
        {"url": "https://bancolombia.com/a", "score": 0.9, "chunk_text": "Chunk A"},
        {"url": "https://bancolombia.com/b", "score": 0.7, "chunk_text": "Chunk B"},
    ]
    result = agent._format_context(items)
    assert "Fuente 1" in result
    assert "Fuente 2" in result


def test_format_context_score_con_dos_decimales(agent):
    items = [{"url": "https://bancolombia.com", "score": 0.9, "chunk_text": "x"}]
    result = agent._format_context(items)
    assert "0.90" in result


def test_should_summarize_turno_cero_no_resume(agent):
    agent._db.execute_query.return_value = [{"summary_text": None, "interactions": 0}]
    assert agent._should_summarize("conv-abc", 0) is False


def test_should_summarize_por_debajo_del_umbral(agent):
    agent._db.execute_query.return_value = [{"summary_text": None, "interactions": 0}]
    assert agent._should_summarize("conv-abc", 3) is False


def test_should_summarize_exactamente_en_el_umbral(agent):
    agent._db.execute_query.return_value = [{"summary_text": None, "interactions": 0}]
    assert agent._should_summarize("conv-abc", 5) is True


def test_should_summarize_multiplo_del_umbral(agent):
    agent._db.execute_query.return_value = [{"summary_text": None, "interactions": 0}]
    assert agent._should_summarize("conv-abc", 10) is True


def test_get_next_message_id_retorna_valor_de_db(agent):
    agent._db.execute_query.return_value = [{"next_id": 7}]
    assert agent._get_next_message_id("conv-xyz") == 7


def test_get_next_message_id_primera_conversacion(agent):
    agent._db.execute_query.return_value = [{"next_id": 1}]
    result = agent._get_next_message_id("nueva-conv")
    assert result == 1


def test_get_history_sin_mensajes_retorna_none(agent):
    agent._db.execute_query.return_value = []
    assert agent._get_history("conv-vacia") is None


def test_get_history_incluye_mensaje_usuario_y_respuesta(agent):
    agent._db.execute_query.return_value = [
        {"human_message": "¿Qué tasas tienen?", "llm_response": "Las tasas dependen del producto."}
    ]
    res = agent._get_history("conv-1")
    assert "¿Qué tasas tienen?" in res
    assert "Las tasas dependen del producto." in res


def test_get_history_formato_usuario_asistente(agent):
    agent._db.execute_query.return_value = [
        {"human_message": "Hola", "llm_response": "Bienvenido"}
    ]
    res = agent._get_history("conv-1")
    assert "Usuario:" in res
    assert "Asistente:" in res

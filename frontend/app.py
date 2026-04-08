import asyncio
import json
import sys
import time
import os

import streamlit as st
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.agent.ai_agent import AIAgent
from backend.core.config_loader import config


st.set_page_config(page_title="Asistente Bancolombia", layout="centered")

# Recurso de MCP
async def _fetch_stats():
    params = StdioServerParameters(
        command=sys.executable,
        args=[config.mcp_server_path],
        env=os.environ
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource("knowledgebase://stats")
            return json.loads(result.contents[0].text)

@st.cache_data(ttl=300)
def get_kb_stats():
    try:
        return asyncio.run(_fetch_stats())
    except Exception as e:
        return {"error": str(e)}

def render_kb_panel():
    stats = get_kb_stats()
    with st.sidebar:
        st.markdown("### 🗄️ Base de conocimiento")
        if "error" in stats:
            st.error("No se pudo conectar al servidor MCP")
            return
        st.metric("Documentos indexados", stats["total_documents"])
        st.metric("Categorías", stats["total_categories"])
        if stats.get("last_updated"):
            st.caption(f"Última actualización: {stats['last_updated'][:10]}")
        st.caption(f"Modelo: `{stats['embedding_model']}`")
        with st.expander("Categorías disponibles"):
            for cat in stats.get("categories", []):
                st.markdown(f"- {cat}")

def render_sources(sources):
    if not sources:
        return
    with st.expander("Fuentes consultadas"):
        for source in sources:
            label = source.get("title") or source.get("url")
            st.markdown(f"- [{label}]({source['url']})")

def render_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                render_sources(msg.get("sources", []))

def check_auth():
    st.title("Asistente Bancolombia")
    st.markdown("Ingresa la contraseña para continuar.")

    password = st.text_input("Contraseña", type="password", key="password_input")
    if st.button("Ingresar"):
        if password == config.env("APP_PASSWORD"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Intenta de nuevo.")

def init_session():
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(int(time.time() * 1000))
        st.session_state.messages = []
        st.session_state.agent = AIAgent()

def handle_input(user_input: str):
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            response = st.session_state.agent.call(
                question=user_input,
                conversation_id=st.session_state.conversation_id,
            )

        st.write(response["answer"])
        render_sources(response.get("sources", []))

    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"],
        "sources": response.get("sources", []),
    })

def main():
    if not st.session_state.get("authenticated"):
        check_auth()
        return

    init_session()
    render_kb_panel()

    st.title("Asistente Bancolombia")
    st.caption(f"Sesión: {st.session_state.conversation_id}")

    st.divider()

    render_history()

    user_input = st.chat_input("Escribe tu pregunta sobre productos y servicios de Bancolombia...")
    if user_input:
        handle_input(user_input)


if __name__ == "__main__":
    main()

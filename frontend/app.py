import time

import streamlit as st

from backend.agent.ai_agent import AIAgent
from backend.core.config_loader import config


st.set_page_config(page_title="Asistente Bancolombia", layout="centered")


def check_auth():
    st.title("Asistente Bancolombia")
    st.markdown("Ingresa la contraseña para continuar.")

    password = st.text_input("Contraseña", type="password", key="password_input")
    if st.button("Ingresar"):
        if password == config.env('APP_PASSWORD'):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Intenta de nuevo.")


def init_session():
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(int(time.time() * 1000))
        st.session_state.messages = []
        st.session_state.agent = AIAgent()


def render_sources(sources: list):
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

    st.title("Asistente Bancolombia")
    st.caption(f"Sesión: {st.session_state.conversation_id}")

    st.divider()

    render_history()

    user_input = st.chat_input("Escribe tu pregunta sobre productos y servicios de Bancolombia...")
    if user_input:
        handle_input(user_input)


if __name__ == "__main__":
    main()
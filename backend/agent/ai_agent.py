import time
from datetime import datetime, timezone

from backend.factories.llm_factory import LLMFactory
from backend.rag.retriever import Retrieve
from backend.core.prompt_loader import PromptLoader
from backend.factories.db_factory import DBFactory
from backend.core.models import ConversationMessage
from backend.core.config_loader import config


class AIAgent:
    
    def __init__(self):
        self._llm = LLMFactory.create()
        self._db = DBFactory.create()
        self._prompt_loader = PromptLoader()
        self._retriever = Retrieve()

    def _save_message(self, message):
        self._db.execute_query(
            f"""
            INSERT INTO {config.sql_lite_conversation_table} VALUES (
                :conversation_id,
                :message_id,
                :message_timestamp,
                :human_message,
                :llm_response,
                :input_tokens,
                :output_tokens,
                :model_name,
                :prompt_version,
                :interaction_time
            )
            """, {
            "conversation_id": message.conversation_id,
            "message_id": message.message_id,
            "message_timestamp": message.message_timestamp,
            "human_message": message.human_message,
            "llm_response": message.llm_response,
            "input_tokens": message.input_tokens,
            "output_tokens": message.output_tokens,
            "model_name": message.model_name,
            "prompt_version": message.prompt_version,
            "interaction_time": message.interaction_time

        })
        
    def _get_next_message_id(self, conversation_id):
        result = self._db.execute_query(
            f"""
            SELECT COALESCE(MAX(message_id), 0) + 1 AS next_id
            FROM {config.sql_lite_conversation_table}
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )
        return result[0]["next_id"]
    
    def _get_history(self, conversation_id):
        limit = config.conversation_history_limit
        result = self._db.execute_query(
            f"""
            SELECT human_message, llm_response
            FROM {config.sql_lite_conversation_table}
            WHERE conversation_id = ?
            ORDER BY message_id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        )
 
        if not result:
            return None

        result = list(reversed(result))
 
        conversation_elements = []
        for conversation in result:
            conversation_elements.append(f"Usuario: {conversation['human_message']}")
            if conversation["llm_response"]:
                conversation_elements.append(f"Asistente: {conversation['llm_response']}")
 
        return "\n".join(conversation_elements)

    def _format_context(self, results):
        if not results:
            return None

        elements = []
        
        for i, item in enumerate(results, start=1):
            url   = item["url"] if isinstance(item, dict) else item.url
            score = item["score"] if isinstance(item, dict) else item.score
            text  = item["chunk_text"] if isinstance(item, dict) else item.chunk_text
            elements.append(
                f"-- Fuente {i} --\n"
                f"URL: {url}\n"
                f"Score: {score:.2f}\n"
                f"{text.strip()}"
            )
        return "\n\n".join(elements)

    def call(self, question, conversation_id):
        
        time_start = time.perf_counter()
        
        # Recuperar historial de conversación
        history = self._get_history(conversation_id)
        
        # Recuperar contenido de Base de Datos Vectorial
        retrieval_results = self._retriever.retrieve(question)
        retrieval_results = self._format_context(retrieval_results)
        
        # Constrir prompt
        system_prompt = self._prompt_loader.system_prompt
        user_prompt = self._prompt_loader.create_user_prompt(
            history = history,
            context = retrieval_results,
            question = question
        )
        
        # Generar respuesta del LLM
        llm_response = self._llm.generate(system_prompt, user_prompt)
        interaction_time = time.perf_counter() - time_start

        # Persistir resultados
        message_id = self._get_next_message_id(conversation_id)
        self._save_message(
            ConversationMessage(
                conversation_id=conversation_id,
                message_id=message_id,
                message_timestamp = datetime.now(timezone.utc).isoformat(),
                human_message=question,
                llm_response=llm_response.content,
                input_tokens=llm_response.input_tokens,
                output_tokens=llm_response.output_tokens,
                model_name=llm_response.model,
                prompt_version=self._prompt_loader.prompt_version,
                interaction_time = round(interaction_time, 2),
            )
        )

        return {
            "answer": llm_response.content,
        }
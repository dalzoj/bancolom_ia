from datetime import datetime, timezone

from backend.factories.llm_factory import LLMFactory
from backend.rag.retriever import Retriever
from backend.core.prompt_loader import PromptLoader
from backend.factories.db_factory import DBFactory
from backend.core.models import ConversationMessage
from backend.core.config_loader import config


class AIAgent:
    
    def __init__(self):
        self._llm = LLMFactory.create()
        self._db = DBFactory.create()
        self._prompt_loader = PromptLoader()
        self._retriever = Retriever()

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
                :prompt_version
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

        })
        

    def _get_next_message_id(self, conversation_id):
        result = self._db.execute_query(
            f"""
            SELECT MAX(message_id) as max_id 
            FROM {config.sql_lite_conversation_table}
            WHERE conversation_id = ?
            """,
            (conversation_id,))
        
        current_max = result[0]["max_id"] if result else None
        return (current_max + 1) if current_max is not None else 1

    def call(self, question, conversation_id = 0):
        
        #### ------------------ PROVISIONAL
        history = None
        
        # Recuperar contenido de Base de Datos Vectorial
        retrieval_results = self._retriever.retriever(question)
        
        # Constrir prompting
        system_prompt = self._prompt_loader.system_prompt
        
        user_prompt = self._prompt_loader.create_user_prompt(
            history = history,
            context = retrieval_results,
            question = question
        )
        
        # Generar respuesta del LLM
        llm_response = self._llm.generate(system_prompt, user_prompt)

        # Persistir resultados
        message_id = self._get_next_message_id(conversation_id)
        self._save_message(
            ConversationMessage(
                conversation_id = conversation_id,
                message_id = message_id,
                message_timestamp = datetime.now(timezone.utc).isoformat(),
                human_message = question,
                llm_response = llm_response.content,
                input_tokens = llm_response.input_tokens,
                output_tokens = llm_response.output_tokens,
                model_name = llm_response.model,
                prompt_version = self._prompt_loader.prompt_version,
            )
        )

        return {
            "answer": llm_response.content,
        }
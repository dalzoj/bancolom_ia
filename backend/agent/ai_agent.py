import asyncio
import json
import sys
import time
from datetime import datetime, timezone

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.factories.llm_factory import LLMFactory
from backend.core.prompt_loader import PromptLoader
from backend.factories.db_factory import DBFactory
from backend.core.models import ConversationMessage, LLMFirstTurnResponse, LLMResponse
from backend.core.config_loader import config


class AIAgent:
    
    def __init__(self):
        self._llm = LLMFactory.create()
        self._db = DBFactory.create()
        self._prompt_loader = PromptLoader()
        self._mcp_server_params = StdioServerParameters(
            command=sys.executable,
            args=[config.mcp_server_path],
        )
    
    # -- MPC Helpers

    async def _run_mcp_turn(self, tool_calls_to_execute):
        async with stdio_client(self._mcp_server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Listar tools
                result = await session.list_tools()
                mcp_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema or {
                                "type": "object",
                                "properties": {},
                            },
                        },
                    }
                    for tool in result.tools
                ]

                # Ejecutar las tool_calls si las hay
                tool_results = []
                for tool_call in tool_calls_to_execute:
                    raw = await session.call_tool(tool_call.tool_name, tool_call.tool_args)
                    if raw.isError:
                        payload = {
                            "error": f"El servidor MCP reportó un error en '{tool_call.tool_name}'.",
                            "results": [],
                        }
                    else:
                        payload = json.loads(raw.content[0].text)
                    tool_results.append((tool_call, payload))

                return mcp_tools, tool_results
    
    def _build_tool_messages(self, base_messages, first_response, tool_results):

        messages = list(base_messages)

        messages.append({
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.tool_name,
                        "arguments": json.dumps(tc.tool_args, ensure_ascii=False),
                    },
                }
                for tc in first_response.tool_calls
            ],
            "tool_plan": first_response.tool_plan,
        })

        for tc, result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        return messages

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

        # Recuperar historial de conversación (memoria de corto plazo)
        history = self._get_history(conversation_id)

        # Obtener tools disponibles del servidor MCP
        mcp_tools, _ = asyncio.run(self._run_mcp_turn([]))

        # Construir el mensaje de usuario con historial embebido
        system_prompt = self._prompt_loader.system_prompt
        user_content  = self._prompt_loader.create_user_prompt(
            history=history,
            question=question,
        )
        messages = [{"role": "user", "content": user_content}]

        # Primer llamado: el LLM decide qué tool invocar o responde directo
        first_response = self._llm.first_step_generate(system_prompt, messages, mcp_tools)

        retrieval_results = []

        if first_response.has_tool_calls:
            
            # Ejecución de tools
            _, tool_results = asyncio.run(self._run_mcp_turn(first_response.tool_calls))
            
            retrieval_results = []
            for tool_call, result in tool_results:
                if tool_call.tool_name == "search_knowledge_base":
                    retrieval_results = result.get("results", [])

            # Segundo llamado: el LLM genera la respuesta final con los resultados
            messages_with_results = self._build_tool_messages(messages, first_response, tool_results)
            llm_response = self._llm.final_step_generate(system_prompt, messages_with_results, mcp_tools)

        else:
            # Respuesta sencilla del LLM
            llm_response = LLMResponse(
                content=first_response.content,
                input_tokens=first_response.input_tokens,
                output_tokens=first_response.output_tokens,
                model=first_response.model,
            )

        interaction_time = time.perf_counter() - time_start

        sources = [
            {
                "url": item["url"],
                "title": item["title"],
                "category": item["category"],
            }
            for item in retrieval_results
        ]

        # Persistir turno de conversación
        message_id = self._get_next_message_id(conversation_id)
        self._save_message(
            ConversationMessage(
                conversation_id=conversation_id,
                message_id=message_id,
                message_timestamp=datetime.now(timezone.utc).isoformat(),
                human_message=question,
                llm_response=llm_response.content,
                input_tokens=llm_response.input_tokens,
                output_tokens=llm_response.output_tokens,
                model_name=llm_response.model,
                prompt_version=self._prompt_loader.prompt_version,
                interaction_time=round(interaction_time, 2),
            )
        )

        return {
            "answer":  llm_response.content,
            "sources": sources,
        }
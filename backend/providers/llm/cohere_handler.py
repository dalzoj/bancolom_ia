import sys
import json

from cohere import ClientV2

from backend.interfaces.llm_interface import LLMInterface
from backend.core.config_loader import config
from backend.core.models import LLMResponse, LLMToolCall, LLMFirstTurnResponse


class CohereHandler(LLMInterface):

    def __init__(self):
        self._client=ClientV2(api_key=config.env("COHERE_API_KEY"))
        self._model=config.llm_model
        self._max_tokens=config.llm_max_tokens
        self._temperature=config.llm_temperature

    def health(self):
        try:
            self._client.models.list()
            print("INFO: Cohere LLM conectado correctamente.", file=sys.stderr)
            return True
        except Exception as e:
            print(f"ERROR: Cohere LLM no disponible — {e}", file=sys.stderr)
            return False

    def generate(self, system_prompt, user_prompt):
        response=self._client.chat(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return LLMResponse(
            content=response.message.content[0].text,
            input_tokens=response.usage.billed_units.input_tokens,
            output_tokens=response.usage.billed_units.output_tokens,
            model=self._model
        )

    def first_step_generate(self, system_prompt, messages, tools):
        response = self._client.chat(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            tools=tools,
            messages=[
                {"role": "system", "content": system_prompt}
                ] + messages,
        )

        tool_calls = None

        if response.message.tool_calls:
            tool_calls = [
                LLMToolCall(
                    id=tc.id,
                    tool_name=tc.function.name,
                    tool_args=json.loads(tc.function.arguments),
                )
                for tc in response.message.tool_calls
            ]

        content = None

        if response.message.content:
            content = response.message.content[0].text

        return LLMFirstTurnResponse(
            tool_calls=tool_calls,
            tool_plan=response.message.tool_plan,
            content=content,
            input_tokens=response.usage.billed_units.input_tokens,
            output_tokens=response.usage.billed_units.output_tokens,
            model=self._model,
        )

    def final_step_generate(self, system_prompt, messages, tools):
        response = self._client.chat(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            tools=tools,
            messages=[
                {"role": "system", "content": system_prompt}
                ] + messages,
        )

        return LLMResponse(
            content=response.message.content[0].text,
            input_tokens=response.usage.billed_units.input_tokens,
            output_tokens=response.usage.billed_units.output_tokens,
            model=self._model,
        )

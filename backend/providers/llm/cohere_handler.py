from cohere import ClientV2

from backend.interfaces.llm_interface import LLMInterface
from backend.core.config_loader import config
from backend.core.models import LLMResponse


class CohereHandler(LLMInterface):

    def __init__(self):
        self._client=ClientV2(api_key=config.env("COHERE_API_KEY"))
        self._model=config.llm_model
        self._max_tokens=config.llm_max_tokens
        self._temperature=config.llm_temperature

    def health(self):
        try:
            self._client.models.list()
            print("INFO: Cohere LLM conectado correctamente.")
            return True
        except Exception as e:
            print(f"ERROR: Cohere LLM no disponible — {e}")
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
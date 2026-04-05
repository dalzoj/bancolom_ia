import yaml

from backend.core.config_loader import config


class PromptLoader:
    
    def __init__(self):
        self._name = config.prompt_name
        self._data = self._load()
        
    def _load(self):
        path = f"backend/prompts/{self._name}.yml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def create_user_prompt(self, history, context, question):
        prompt_template = self._data["user_template"]
        return prompt_template.format(
            history = history or "Sin historial previo en esta conversación.",
            context = context or "Sin contexto recuperado.",
            question = question
        ).strip()

    @property
    def system_prompt(self):
        return self._data["system"].strip()
    @property
    def prompt_version(self):
        return self._data["metadata"]["version"]
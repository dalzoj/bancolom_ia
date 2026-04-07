import yaml

from backend.core.config_loader import config


class PromptLoader:
    
    def __init__(self):
        self._name = config.prompt_name
        self._data = self._load()
        
    def _load(self):
        print(f'INFO: Cargado modelo {self._name}')
        path = f"backend/prompts/{self._name}.yml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def create_user_prompt(self, history, question, summary=None):
        return self._data["user_template"].format(
            summary=summary or "Sin resumen previo en esta conversación.",
            history=history or "Sin historial previo en esta conversación.",
            question=question,
        ).strip()

    @property
    def system_prompt(self):
        return self._data["system"].strip()
    
    @property
    def prompt_version(self):
        return self._data["metadata"]["version"]
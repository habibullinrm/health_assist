"""
Модуль для работы с промптами
"""
from pathlib import Path
import yaml
from typing import Dict, Any


class PromptLoader:
    """Загрузчик промптов из YAML файлов"""

    def __init__(self, prompts_dir: Path = None):
        """
        Инициализация загрузчика

        Args:
            prompts_dir: Директория с промптами
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent
        self.prompts_dir = prompts_dir

    def load_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Загрузить промпт из YAML файла

        Args:
            prompt_name: Имя файла промпта (без расширения)

        Returns:
            Словарь с конфигурацией промпта
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.yaml"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_config = yaml.safe_load(f)

        return prompt_config

    def format_user_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Форматировать пользовательский промпт с подстановкой параметров

        Args:
            prompt_name: Имя промпта
            **kwargs: Параметры для подстановки в шаблон

        Returns:
            Отформатированный пользовательский промпт
        """
        prompt_config = self.load_prompt(prompt_name)
        user_prompt_template = prompt_config.get('user_prompt_template', '')

        return user_prompt_template.format(**kwargs)

    def get_system_prompt(self, prompt_name: str) -> str:
        """
        Получить системный промпт

        Args:
            prompt_name: Имя промпта

        Returns:
            Системный промпт
        """
        prompt_config = self.load_prompt(prompt_name)
        return prompt_config.get('system_prompt', '')

    def get_response_schema(self, prompt_name: str) -> Dict[str, Any]:
        """
        Получить JSON схему ответа

        Args:
            prompt_name: Имя промпта

        Returns:
            JSON схема ответа
        """
        prompt_config = self.load_prompt(prompt_name)
        return prompt_config.get('response_schema', {})

    def get_llm_parameters(self, prompt_name: str) -> Dict[str, Any]:
        """
        Получить параметры для LLM

        Args:
            prompt_name: Имя промпта

        Returns:
            Параметры для LLM
        """
        prompt_config = self.load_prompt(prompt_name)
        return prompt_config.get('llm_parameters', {})

    def get_examples(self, prompt_name: str) -> list:
        """
        Получить примеры для few-shot learning

        Args:
            prompt_name: Имя промпта

        Returns:
            Список примеров
        """
        prompt_config = self.load_prompt(prompt_name)
        return prompt_config.get('examples', [])


# Глобальный экземпляр загрузчика
prompt_loader = PromptLoader()


def load_treatment_plan_prompt(treatment_plan_text: str) -> tuple[str, str, Dict[str, Any]]:
    """
    Загрузить промпт для извлечения информации из плана лечения

    Args:
        treatment_plan_text: Текст плана лечения

    Returns:
        Кортеж (system_prompt, user_prompt, llm_parameters)
    """
    system_prompt = prompt_loader.get_system_prompt('extract_treatment_plan')
    user_prompt = prompt_loader.format_user_prompt(
        'extract_treatment_plan',
        treatment_plan_text=treatment_plan_text
    )
    llm_parameters = prompt_loader.get_llm_parameters('extract_treatment_plan')

    return system_prompt, user_prompt, llm_parameters
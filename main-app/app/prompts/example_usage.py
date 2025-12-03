"""
Пример использования промпта для извлечения информации из плана лечения
"""
import json
from app.prompts import load_treatment_plan_prompt, prompt_loader


def extract_treatment_info(treatment_plan_text: str) -> dict:
    """
    Извлечь структурированную информацию из плана лечения

    Args:
        treatment_plan_text: Текст плана лечения

    Returns:
        Словарь с извлеченной информацией
    """
    # Загружаем промпт
    system_prompt, user_prompt, llm_parameters = load_treatment_plan_prompt(treatment_plan_text)

    print("=" * 80)
    print("СИСТЕМНЫЙ ПРОМПТ:")
    print("=" * 80)
    print(system_prompt)
    print()

    print("=" * 80)
    print("ПОЛЬЗОВАТЕЛЬСКИЙ ПРОМПТ:")
    print("=" * 80)
    print(user_prompt)
    print()

    print("=" * 80)
    print("ПАРАМЕТРЫ LLM:")
    print("=" * 80)
    print(json.dumps(llm_parameters, indent=2, ensure_ascii=False))
    print()

    # Здесь нужно вызвать LLM (GigaChat или другую модель)
    # Пример:
    # response = gigachat_client.chat(
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     temperature=llm_parameters.get('temperature', 0.1),
    #     max_tokens=llm_parameters.get('max_tokens', 2000)
    # )
    # return json.loads(response.content)

    print("=" * 80)
    print("JSON СХЕМА ОТВЕТА:")
    print("=" * 80)
    response_schema = prompt_loader.get_response_schema('extract_treatment_plan')
    print(json.dumps(response_schema, indent=2, ensure_ascii=False))

    return {}


if __name__ == "__main__":
    # Пример текста плана лечения
    sample_text = """
    ПЛАН ЛЕЧЕНИЯ

    Врач: Иванов Иван Иванович, терапевт
    Медицинский центр "Здоровье"

    Жалобы пациента:
    - Боли в горле
    - Повышенная температура 38.2°C
    - Общая слабость

    Диагноз: Острый фарингит

    Назначения:
    1. Амоксициллин 500 мг по 1 таблетке 3 раза в день после еды, курс 7 дней
    2. Ибупрофен 200 мг по 1 таблетке при температуре выше 38°C, не более 3 раз в день
    3. Полоскание горла раствором фурацилина 3-4 раза в день

    Направления на обследования:
    - Общий анализ крови (сдать натощак)
    - Мазок из зева на флору

    Направления к специалистам:
    - Консультация ЛОР-врача (при отсутствии улучшения через 5 дней)

    Рекомендации:
    - Обильное теплое питье
    - Голосовой покой
    - Избегать переохлаждения

    Контрольный осмотр через 7 дней
    """

    extract_treatment_info(sample_text)
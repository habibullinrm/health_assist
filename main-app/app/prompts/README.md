# Промпты для извлечения информации из планов лечения

Эта директория содержит YAML-файлы с промптами для извлечения структурированной информации из медицинских документов.

## Структура файла промпта

Каждый YAML-файл промпта содержит:

- `name` - название промпта
- `description` - описание назначения промпта
- `version` - версия промпта
- `system_prompt` - системный промпт для LLM
- `user_prompt_template` - шаблон пользовательского промпта с параметрами
- `response_schema` - JSON Schema ожидаемого ответа
- `examples` - примеры для few-shot learning
- `llm_parameters` - рекомендуемые параметры для LLM
- `post_processing` - список шагов постобработки

## Доступные промпты

### extract_treatment_plan.yaml

Извлекает из текста плана лечения:

1. **Врач** - специализация, ФИО, медицинское учреждение
2. **Симптомы** - описание симптомов и их выраженность
3. **Направления к врачам** - специализация, цель, срочность
4. **Направления на обследования** - название, тип, подготовка, срок
5. **Лекарства** - название, дозировка, частота, время приема, длительность, форма выпуска

## Использование

### Базовое использование

```python
from app.prompts import load_treatment_plan_prompt

# Текст плана лечения
treatment_text = """
ПЛАН ЛЕЧЕНИЯ
Врач: Иванов И.И., терапевт
...
"""

# Загружаем промпт
system_prompt, user_prompt, llm_parameters = load_treatment_plan_prompt(treatment_text)

# Используем с LLM (например, GigaChat)
response = gigachat_client.chat(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=llm_parameters.get('temperature', 0.1),
    max_tokens=llm_parameters.get('max_tokens', 2000)
)

# Парсим JSON ответ
import json
result = json.loads(response.content)
```

### Продвинутое использование

```python
from app.prompts import prompt_loader

# Загружаем конкретные части промпта
system_prompt = prompt_loader.get_system_prompt('extract_treatment_plan')
response_schema = prompt_loader.get_response_schema('extract_treatment_plan')
examples = prompt_loader.get_examples('extract_treatment_plan')

# Форматируем пользовательский промпт
user_prompt = prompt_loader.format_user_prompt(
    'extract_treatment_plan',
    treatment_plan_text=your_text
)
```

## Формат ответа

Пример успешного ответа:

```json
{
  "doctor": {
    "full_name": "Иванов И.И.",
    "specialization": "Терапевт",
    "medical_organization": "Поликлиника №5"
  },
  "symptoms": [
    {
      "symptom": "повышенная температура 38.5°C",
      "severity": "умеренная"
    }
  ],
  "referrals": [
    {
      "specialization": "Кардиолог",
      "purpose": "консультация",
      "urgency": "плановый"
    }
  ],
  "examinations": [
    {
      "name": "Общий анализ крови",
      "type": "анализ",
      "preparation": "сдать натощак",
      "deadline": "в течение 3 дней"
    }
  ],
  "medications": [
    {
      "name": "Амоксициллин",
      "dosage": "500 мг",
      "frequency": "3 раза в день",
      "timing": "после еды",
      "duration": "7 дней",
      "form": "таблетки",
      "special_instructions": null
    }
  ],
  "additional_recommendations": [
    "Обильное питье",
    "Постельный режим"
  ],
  "metadata": {
    "confidence": "высокая",
    "notes": null
  }
}
```

## Тестирование

Запустите пример использования:

```bash
cd main-app
python -m app.prompts.example_usage
```

Это выведет системный и пользовательский промпты, а также JSON схему ответа.

## Интеграция с обработчиком PDF

Пример интеграции с `pdf_processor.py`:

```python
from app.services.pdf_processor import process_treatment_plan_pdf
from app.prompts import load_treatment_plan_prompt
import json

# 1. Извлекаем текст из PDF
pdf_result = process_treatment_plan_pdf("/path/to/plan.pdf")

if pdf_result['status'] == 'success':
    text = pdf_result['data']['text']

    # 2. Загружаем промпт
    system_prompt, user_prompt, llm_params = load_treatment_plan_prompt(text)

    # 3. Отправляем в LLM
    response = gigachat_client.chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        **llm_params
    )

    # 4. Парсим результат
    structured_data = json.loads(response.content)

    print(f"Врач: {structured_data['doctor']['full_name']}")
    print(f"Лекарств назначено: {len(structured_data['medications'])}")
```

## Рекомендации

1. **Temperature**: Используйте низкую температуру (0.1-0.2) для более детерминированных результатов
2. **Валидация**: Всегда валидируйте JSON ответ по схеме перед использованием
3. **Обработка ошибок**: Учитывайте, что LLM может вернуть невалидный JSON
4. **Few-shot learning**: Используйте примеры из промпта для улучшения качества извлечения
5. **Постобработка**: Нормализуйте извлеченные данные (приводите названия лекарств к единому формату, и т.д.)

## Обновление промптов

При изменении промпта:

1. Увеличьте номер версии в поле `version`
2. Протестируйте на примерах из поля `examples`
3. Обновите документацию при необходимости

## Добавление новых промптов

Чтобы добавить новый промпт:

1. Создайте файл `your_prompt_name.yaml` в этой директории
2. Следуйте структуре существующих промптов
3. Добавьте примеры в поле `examples`
4. Обновите этот README
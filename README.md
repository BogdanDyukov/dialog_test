# Проверка игровых диалогов

Структура проекта:

- `analyzers/` — запускаемые анализаторы квестов и кат-сцен;
- `dialogue_checker/` — общие Python-модули и правила проверок;
- `data/` — словари и исключения;
- `prompts/` — промпты для обработки текстов;
- `reports/` — результаты работы анализаторов;
- `scripts/` — вспомогательные и экспериментальные скрипты.

Анализаторы запускаются из корня проекта:

```bash
python3 analyzers/quest_analyser.py
python3 analyzers/cutscenes_analyser.py
```

Также поддерживается запуск через `python3 -m analyzers.quest_analyser` и
`python3 -m analyzers.cutscenes_analyser`.

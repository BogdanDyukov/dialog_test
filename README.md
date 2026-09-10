# Проверка игровых диалогов

## Настройка проекта

1) Установка зависимостей:

В корне проекта:

```bash
python3 -m venv venv
source venv/bin/Activate
pip freeze > requirements.txt
```

2) Первый запуск (из корня проекта):

```bash
python3 run_analyser.py
```

Создастся `config.json`, где надо задать пути к файлам (папка с названиями квестов и папка с диалогами):

```json
{
  "quest_titles_dir": "/Users/username/game-project/configs/quests/0001_name",
  "cutscenes_dir": "/Users/username/game-project/configs/cutscenes"
}
```

Оба пути должны быть абсолютными.

3) Последующие запуски (из корня проекта):

```bash
python3 run_analyser.py
```

Сначала нужно выбрать, что проверять: диалоги, названия квестов или всё сразу,
а затем ввести номер локации.

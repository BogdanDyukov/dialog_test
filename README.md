# Проверка игровых диалогов

Пути к игровому проекту задаются в `config.json`:

```json
{
  "quest_titles_dir": "/Users/username/game-project/configs/quests/0001_name",
  "cutscenes_dir": "/Users/username/game-project/configs/cutscenes"
}
```

Оба пути должны быть абсолютными.

Общий интерактивный запуск из корня проекта:

```bash
python3 run_analyser.py
```

Сначала нужно выбрать, что проверять: диалоги, названия квестов или всё сразу,
а затем ввести номер локации.

Анализаторы также можно запускать отдельно. Номер локации разрешено передать
аргументом или ввести после запуска:

```bash
python3 analyzers/quest_analyser.py 16
python3 analyzers/cutscenes_analyser.py 16
```

Техничка (для Богдана)

```bash
%pip install -r requirements.txt
```

```bash
{
  "quest_titles_dir": "/Users/bogdan.dyukov/merge2/configs/quests/0001_name",
  "cutscenes_dir": "/Users/bogdan.dyukov/merge2/configs/cutscenes"
}
```
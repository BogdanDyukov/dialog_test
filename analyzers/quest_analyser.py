# /Users/bogdan.dyukov/merge2/configs/quests/0001_name/0010.conf.js

from pathlib import Path
import sys
import re
import json5
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dialogue_checker.yo import load_yo_dictionary, yoficate_text
import requests
from dialogue_checker.alena_skins import (
    ALENA_SKINS,
    get_expected_alena_skin_sequence,
)
from dialogue_checker.morph_analyzer import (
    is_speller_false_positive,
    title_exceptions,
)

DATA_DIR = PROJECT_ROOT / "data"

n = int(input("Номер локации: "))

filename = f"{n:04d}.conf.js"
filepath = Path("/Users/bogdan.dyukov/merge2/configs/quests/0001_name") / filename

if not filepath.exists():
    print(f"Файл не найден: {filepath}")
    exit(1)

# Читаем файл
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Добавляем пропущенные запятые между полями
text = re.sub(
    r'(".*?"|\d+|true|false|null|\]|\})\s*\n(\s*"[^"]+"\s*:)',
    r'\1,\n\2',
    text
)

# Убираем случайные двойные запятые
text = re.sub(r",\s*,+", ",", text)

data = json5.loads(text)

quests = []

for index, q in enumerate(data.get("quests", []), start=1):
    if not isinstance(q, dict):
        print(
            f"\t- Квест {index}: ожидался объект, "
            f"получено {type(q).__name__}"
        )
        continue

    quests.append({
        "id": q.get("id"),
        "local_number": index,
        "price_money": q.get("price_money"),
        "rewards": q.get("rewards") or [],
        "character": q.get("character") or "",
        "title": q.get("title") or "",
        "cutscene": q.get("cutscene") or ""
    })


def format_quest_label(quest):
    local_number = quest["local_number"]
    quest_id = quest["id"]

    if quest_id is None:
        return f"Квест {local_number} (без id)"

    return f"Квест {local_number} (id={quest_id})"


print("\n--- ФАЙЛ С НАЗВАНИЯМИ КАТСЦЕН И РЕВАРДАМИ ---")





print("\n1 НАЛИЧИЕ ПУСТЫХ ЗНАЧЕНИЙ")

found = False

for quest in quests:
    for field in (
        "id",
        "price_money",
        "rewards",
        "title",
        "character",
        "cutscene",
    ):
        value = quest.get(field)

        if (
            value is None
            or value == []
            or (isinstance(value, str) and not value.strip())
        ):
            found = True
            print(
                f'\t- {format_quest_label(quest)}: '
                f'пустое или отсутствующее поле "{field}"'
            )

if not found:
    print("\t- Не найдено")


print("\n2 КОРРЕКТНОСТЬ price_money")

found = False

for quest in quests:
    price_money = quest.get("price_money")

    # Отсутствующее значение уже выводится в проверке пустых полей.
    if price_money is None:
        continue

    if (
        isinstance(price_money, bool)
        or not isinstance(price_money, int)
        or price_money <= 0
    ):
        found = True
        print(
            f'\t- {format_quest_label(quest)}: price_money={price_money!r}; '
            "ожидалось целое число больше нуля"
        )

if not found:
    print("\t- Не найдено")






print("\n3 НАЛИЧИЕ НЕДОПУСТИМЫХ СИМВОЛОВ В title")

found = False

for quest in quests:
    title = quest.get("title", "")

    bad_chars = sorted(set(re.findall(r"[^А-Яа-яЁё !?\-]", title)))

    if bad_chars:
        found = True
        print(
            f'\t- {format_quest_label(quest)}: title={repr(title)} '
            f'содержит символы: {", ".join(repr(c) for c in bad_chars)}'
        )

if not found:
    print("\t- Не найдено")





print("\n4 ПРОВЕРКА ОФОРМЛЕНИЯ title")

found = False

for quest in quests:
    title = quest.get("title", "")
    errors = []

    if title != title.strip():
        errors.append("пробел в начале или конце")

    if "  " in title:
        errors.append("двойной пробел")

    if re.search(r"(?<![А-Яа-яЁё])-|-(?![А-Яа-яЁё])", title):
        errors.append(
            "дефис должен находиться между русскими буквами без пробелов"
        )

    if re.search(r"[!?](?![!?]*$)", title):
        errors.append(
            "восклицательный или вопросительный знак находится не в конце"
        )

    if errors:
        found = True
        print(f'\t- {format_quest_label(quest)}: title={title!r}')

        for error in errors:
            print(f"\t\t- {error}")

if not found:
    print("\t- Не найдено")


# https://github.com/Text-extend-tools/python-yoficator/blob/master/yo.dat
print("\n5 НАЛИЧИЕ 'Е' ВМЕСТО 'Ë' В title (ËТИФИКАТОР)")

found = False

yo_dictionary = load_yo_dictionary(DATA_DIR / "yo.dat")

for quest in quests:
    title = quest["title"]
    yoficated = yoficate_text(title, yo_dictionary)

    if title != yoficated:
        found = True
        print(
            f'\t- {format_quest_label(quest)}: "{title}" -> "{yoficated}"'
        )

if not found:
    print("\t- Не найдено")






print("\n6 НАЛИЧИЕ 'ВСЕ' ИЛИ 'ВСЁ' В title (РУЧНАЯ ПРОВЕРКА)")

found = False

for quest in quests:
    title = quest["title"]

    if re.search(r"\bвс[её]\b", title, re.IGNORECASE):
        found = True
        print(f'\t- {format_quest_label(quest)}: "{title}"')

if not found:
    print("\t- Не найдено")


print("\n7 ОТСУТСТВИЕ @item/stock/xp СО ЗНАЧЕНИЕМ 15")

found = False

for quest in quests:
    rewards = quest.get("rewards", [])

    has_xp_reward = any(
        reward.get("proto_id") == "@item/stock/xp"
        and reward.get("amount") == 15
        for reward in rewards
    )

    if not has_xp_reward:
        found = True
        print(
            f'\t- {format_quest_label(quest)}: отсутствует XP ревард '
            f'{{proto_id="@item/stock/xp", amount=15}}'
        )

if not found:
    print("\t- Не найдено")







# https://docs.google.com/spreadsheets/d/1JCbNlZfGQZyrjahTiBKXEylgyg-k2jt-Tzp6qgejdqY/edit?gid=647621717#gid=647621717
print("\n8 ПРОВЕРКА ПОРЯДКА СКИНОВ АЛЁНКИ В character")

found = False

expected_sequence = get_expected_alena_skin_sequence(n)

if expected_sequence is None:
    found = True
    print(f"\t- Для локации {n} не задан порядок скинов Алёнки")
else:
    known_skins = set(ALENA_SKINS.values())
    actual_sequence = []
    transition_quests = []

    for quest in quests:
        character = quest.get("character", "")

        if not character.startswith("@character/alena"):
            continue

        if character not in known_skins:
            found = True
            print(
                f'\t- {format_quest_label(quest)}: неизвестный скин '
                f'Алёнки character="{character}"'
            )
            continue

        if not actual_sequence or actual_sequence[-1] != character:
            actual_sequence.append(character)
            transition_quests.append(format_quest_label(quest))

    actual_sequence = tuple(actual_sequence)

    if actual_sequence != expected_sequence:
        found = True

        expected_text = " → ".join(expected_sequence)
        actual_text = " → ".join(actual_sequence) or "скины не встретились"

        print("\t- Нарушен порядок скинов Алёнки")
        print(f"\t\tОжидался: {expected_text}")
        print(f"\t\tПолучен:  {actual_text}")

        if transition_quests:
            print(
                "\t\tСмена скинов в квестах: "
                + ", ".join(map(str, transition_quests))
            )

if not found:
    print("\t- Не найдено")









print("\n9 НАЛИЧИЕ ОРФОГРАФИЧЕСКИХ ОШИБОК В title (ЯНДЕКС СПЕЛЛЕР)")

found = False

titles = [
    quest.get("title", "")
         .replace("\n", " ")
         .strip()
    for quest in quests
]

response = requests.post(
    "https://speller.yandex.net/services/spellservice.json/checkTexts",
    data={
        "text": titles,
        "lang": "ru",
        "format": "plain",
    },
    timeout=10
)

response.raise_for_status()

spell_results = response.json()

if not isinstance(spell_results, list):
    raise RuntimeError(
        "Яндекс Спеллер вернул ответ неожиданного формата: "
        f"ожидался список, получено {type(spell_results).__name__}"
    )

if len(spell_results) != len(quests):
    raise RuntimeError(
        "Яндекс Спеллер вернул неправильное количество результатов: "
        f"отправлено заголовков — {len(quests)}, "
        f"получено результатов — {len(spell_results)}"
    )

for quest, errors in zip(quests, spell_results):
    errors = [
        error for error in errors
        if error.get("word", "").casefold() not in title_exceptions
        and not is_speller_false_positive(error)
    ]

    if not errors:
        continue

    found = True

    print(f'\t- {format_quest_label(quest)}: "{quest["title"]}"')

    for error in errors:
        word = error.get("word")
        suggestions = error.get("s", [])

        if suggestions:
            print(f'\t\t{word} -> {", ".join(suggestions)}')
        else:
            print(f'\t\t{word} -> нет подсказок')

if not found:
    print("\t- Не найдено")

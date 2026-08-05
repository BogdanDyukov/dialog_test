# /Users/bogdan.dyukov/merge2/configs/quests/0001_name/0010.conf.js

from pathlib import Path
import re
import json5
import json
from yo import load_yo_dictionary, yoficate_text
import requests
from pymorphy3 import MorphAnalyzer
from alena_skins import ALENA_SKINS, LOCATION_ALENA_SKINS, get_allowed_alena_skins
from morph_analyzer import title_exceptions

n = int(input("Номер локации: "))

filename = f"{n:04d}.conf.js"
filepath = Path("/Users/bogdan.dyukov/merge2/configs/quests/0001_name") / filename

if not filepath.exists():
    print(f"Файл не найден: {filepath}")
    exit(1)

# Читаем файл
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Удаляем комментарии
text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
text = re.sub(r"//.*", "", text)

# Добавляем пропущенные запятые между полями
text = re.sub(
    r'(".*?"|\d+|true|false|null|\]|\})\s*\n(\s*"[^"]+"\s*:)',
    r'\1,\n\2',
    text
)

# Убираем случайные двойные запятые
text = re.sub(r",\s*,+", ",", text)

data = json5.loads(text)

quests = [
    {
        "id": q["id"],
        "price_money": q["price_money"],
        "rewards": q["rewards"],
        "character": q["character"],
        "title": q["title"],
        "cutscene": q["cutscene"]
    }
    for q in data["quests"]
]

print("\n--- ФАЙЛ С НАЗВАНИЯМИ КАТСЦЕН И РЕВАРДАМИ ---")





print("\n1 НАЛИЧИЕ ПУСТЫХ ЗНАЧЕНИЙ (rewards, title и character, cutscene)")

found = False

for quest in quests:
    for field in ("rewards", "title", "character", "cutscene"):
        value = quest.get(field)

        if value is None or value == "" or value == []:
            found = True
            print(f'\t- Квест {quest["id"]}: пустое поле "{field}"')

if not found:
    print("\t- Не найдено")






print("\n2 НАЛИЧИЕ НЕДОПУСТИМЫХ СИМВОЛОВ В title")

found = False

for quest in quests:
    title = quest.get("title", "")

    bad_chars = sorted(set(re.findall(r"[^А-Яа-яЁё ]", title)))

    if bad_chars:
        found = True
        print(
            f'\t- Квест {quest["id"]}: title={repr(title)} содержит символы: {", ".join(repr(c) for c in bad_chars)}'
        )

if not found:
    print("\t- Не найдено")





# https://github.com/Text-extend-tools/python-yoficator/blob/master/yo.dat
print("\n3 НАЛИЧИЕ 'Е' ВМЕСТО 'Ë' В title (ËТИФИКАТОР)")

found = False

yo_dictionary = load_yo_dictionary("yo.dat")

for quest in quests:
    title = quest["title"]
    yoficated = yoficate_text(title, yo_dictionary)

    if title != yoficated:
        found = True
        print(
            f'\t- Квест {quest["id"]}: "{title}" -> "{yoficated}"'
        )

if not found:
    print("\t- Не найдено")






print("\n4 НАЛИЧИЕ 'ВСЕ' ИЛИ 'ВСЁ' В title (РУЧНАЯ ПРОВЕРКА)")

found = False

for quest in quests:
    title = quest["title"]

    if re.search(r"\bвс[её]\b", title, re.IGNORECASE):
        found = True
        print(f'\t- Квест {quest["id"]}: "{title}"')

if not found:
    print("\t- Не найдено")


print("\n5 НАЛИЧИЕ БУКВЫ 'Ё' В title (РУЧНАЯ ПРОВЕРКА)")

found = False

for quest in quests:
    title = quest["title"]

    if "ё" in title.lower():
        found = True
        print(f'\t- Квест {quest["id"]}: "{title}"')

if not found:
    print("\t- Не найдено")





print("\n6 ОТСУТСТВИЕ @item/stock/xp СО ЗНАЧЕНИЕМ 15")

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
            f'\t- Квест {quest["id"]}: отсутствует XP ревард {{proto_id="@item/stock/xp", amount=15}}'
        )

if not found:
    print("\t- Не найдено")







# https://docs.google.com/spreadsheets/d/1JCbNlZfGQZyrjahTiBKXEylgyg-k2jt-Tzp6qgejdqY/edit?gid=647621717#gid=647621717
print("\n7 ПРОВЕРКА СКИНА АЛЁНКИ В character")

found = False

allowed_skins = get_allowed_alena_skins(n)

if allowed_skins is None:
    found = True
    print(f"\t- Для локации {n} не заданы допустимые скины")
else:
    used_skins = set()

    for quest in quests:
        character = quest.get("character", "")

        if not character.startswith("@character/alena_"):
            continue

        if character in allowed_skins:
            used_skins.add(character)
        else:
            found = True
            print(
                f'\t- Квест {quest["id"]}: недопустимый скин character="{character}", '
                f'допустимо: {", ".join(sorted(allowed_skins))}'
            )

    missing_skins = allowed_skins - used_skins

    for skin in sorted(missing_skins):
        found = True
        print(
            f'\t- В локации {n} не встретился обязательный скин "{skin}"'
        )

if not found:
    print("\t- Не найдено")









print("\n8 НАЛИЧИЕ ОРФОГРАФИЧЕСКИХ ОШИБОК В title (ЯНДЕКС СПЕЛЛЕР)")

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

for quest, errors in zip(quests, spell_results):
    errors = [
        error for error in errors
        if error.get("word", "").lower() not in title_exceptions
    ]

    if not errors:
        continue

    found = True

    print(f'\t- Квест {quest["id"]}: "{quest["title"]}"')

    for error in errors:
        word = error.get("word")
        suggestions = error.get("s", [])

        if suggestions:
            print(f'\t\t{word} -> {", ".join(suggestions)}')
        else:
            print(f'\t\t{word} -> нет подсказок')

if not found:
    print("\t- Не найдено")
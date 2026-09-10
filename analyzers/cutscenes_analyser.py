from pathlib import Path
import sys
import re
import json
import json5
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dialogue_checker.yo import load_yo_dictionary, yoficate_text
from dialogue_checker.morph_analyzer import (
    is_speller_false_positive,
    text_exceptions,
)

DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHARACTER_NAMES_PATH = DATA_DIR / "character_names.json"
EMOTION_DESCRIPTIONS_PATH = DATA_DIR / "emotion_descriptions.json"
UNKNOWN_CHARACTER_NAMES_PATH = REPORTS_DIR / "unknown_character_names.json"

with open(CHARACTER_NAMES_PATH, "r", encoding="utf-8") as f:
    NAME_TO_PREFIX = json.load(f)

with open(EMOTION_DESCRIPTIONS_PATH, "r", encoding="utf-8") as f:
    EMOTION_DESCRIPTIONS = json.load(f)

def prepare_conf_text(text: str) -> str:
    # Удаляем комментарии
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)

    # Удаляем шаблонные вставки вида <%VCLASSID(...)%>
    text = re.sub(r"<%.*?%>", "", text, flags=re.DOTALL)

    # Добавляем пропущенные запятые между полями
    text = re.sub(
        r'(".*?"|\d+|true|false|null|\]|\})\s*\n(\s*"[^"]+"\s*:)',
        r'\1,\n\2',
        text
    )

    # Убираем двойные запятые
    text = re.sub(r",\s*,+", ",", text)

    return text


def load_quest_cutscene_ids(location_id: int) -> dict:
    filename = f"{location_id:04d}.conf.js"
    filepath = Path("/Users/bogdan.dyukov/merge2/configs/quests/0001_name") / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Файл квестов не найден: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    text = prepare_conf_text(text)
    data = json5.loads(text)

    result = {}

    for quest in data["quests"]:
        cutscene = quest.get("cutscene")
        quest_id = quest.get("id")

        if cutscene and quest_id:
            result[cutscene] = quest_id

    return result


def parse_cutscene_file(filepath: Path, cutscene_to_quest_id: dict):
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    alias_match = re.search(
        r"alias\s*=\s*(@cutscenes/[^\s*]+)",
        raw_text
    )

    alias = alias_match.group(1) if alias_match else None
    quest_id = cutscene_to_quest_id.get(alias)

    text = prepare_conf_text(raw_text)
    data = json5.loads(text)

    dialogs = []

    for sequence_item in data.get("sequence", []):

        if "cue" not in sequence_item:
            continue

        dialog_block = []

        for cue in sequence_item["cue"]:

            if "text" not in cue:
                continue

            dialog_block.append({
                "cue_type": cue.get("cue_type"),
                "name": cue.get("name"),
                "text": cue.get("text"),
                "character": cue.get("character"),
                "emotion": cue.get("emotion"),
                "position": cue.get("position"),
            })

        if dialog_block:
            dialogs.append(dialog_block)

    return {
        "id": quest_id,
        "cutscene": alias,
        "dialogs": dialogs
    }


n = int(input("Введите номер локации: "))

cutscenes_dir = Path(
    f"/Users/bogdan.dyukov/merge2/configs/cutscenes/{n:04d}"
)

if not cutscenes_dir.exists():
    print(f"Папка не найдена: {cutscenes_dir}")
    exit(1)

cutscene_to_quest_id = load_quest_cutscene_ids(n)

all_cutscenes = []

for filepath in sorted(cutscenes_dir.glob("*.conf.js")):
    try:
        cutscene = parse_cutscene_file(
            filepath,
            cutscene_to_quest_id
        )

        all_cutscenes.append(cutscene)

    except Exception as e:
        print(f"{filepath.name}: ошибка парсинга ({e})")

total_dialog_blocks = sum(len(c["dialogs"]) for c in all_cutscenes)
total_cues = sum(
    len(dialog)
    for c in all_cutscenes
    for dialog in c["dialogs"]
)

quest_numbers = {
    cutscene["id"]: i
    for i, cutscene in enumerate(all_cutscenes, start=0)
}


print(f"\nВсего катсцен: {len(all_cutscenes)}")
print(f"Всего диалоговых блоков: {total_dialog_blocks}")
print(f"Всего реплик: {total_cues}")





print("\n--- ФАЙЛ С ДИАЛОГАМИ КАТСЦЕН ---")







print("\n1.1 ОГРАНИЧЕНИЕ НА ЧИСЛО СИМВОЛОВ В СТРОКЕ (21/18 СИМВОЛОВ)")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            cue_type = cue.get("cue_type")
            text = cue.get("text", "")

            if cue_type == "SPECH_BUBLE":
                limit = 21
                cue_type_name = "фраза"
            elif cue_type == "THOUGHT_BUBBLE":
                limit = 18
                cue_type_name = "мысль"
            else:
                continue

            for line_index, line in enumerate(text.split("\n"), start=1):
                if len(line) > limit:
                    found = True
                    print(
                        f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                        f'реплика {cue_index}, строка {line_index}: '
                        f'{cue_type_name} более {limit} символов — '
                        f'{len(line)} символов: "{line}"'
                    )

if not found:
    print("\t- Не найдено")






print("\n1.2 ОГРАНИЧЕНИЕ НА ЧИСЛО СТРОК (4/3 СТРОКИ)")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            cue_type = cue.get("cue_type")
            text = cue.get("text", "")

            if cue_type == "SPECH_BUBLE":
                limit = 4
                cue_type_name = "фраза"
            elif cue_type == "THOUGHT_BUBBLE":
                limit = 3
                cue_type_name = "мысль"
            else:
                continue

            lines = text.split("\n")

            if len(lines) > limit:
                found = True
                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: '
                    f'{cue_type_name} содержит {len(lines)} строк '
                    f'(лимит {limit})'
                )

if not found:
    print("\t- Не найдено")






print("\n1.3 ОГРАНИЧЕНИЕ НА ОБЩЕЕ ЧИСЛО СИМВОЛОВ (84/54 СИМВОЛА)")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            cue_type = cue.get("cue_type")
            text = cue.get("text", "")

            if cue_type == "SPECH_BUBLE":
                limit = 84
                cue_type_name = "фраза"
            elif cue_type == "THOUGHT_BUBBLE":
                limit = 54
                cue_type_name = "мысль"
            else:
                continue

            total_length = len(text.replace("\n", ""))

            if total_length > limit:
                found = True
                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: '
                    f'{cue_type_name} содержит {total_length} символов '
                    f'(лимит {limit})'
                )

if not found:
    print("\t- Не найдено")





print("\n1.4 ОГРАНИЧЕНИЕ НА ЧИСЛО РЕПЛИК В ДИАЛОГЕ (ДО 20)")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):

        replica_count = len(dialog)

        if replica_count > 20:
            found = True
            print(
                f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}: '
                f'{replica_count} реплик (лимит 20)'
            )

if not found:
    print("\t- Не найдено")













print("\n2 ПУСТЫЕ cue_type, name, text, character, emotion, position")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):

            empty_fields = []

            for field in (
                "cue_type",
                "name",
                "text",
                "character",
                "emotion",
                "position"
            ):
                value = cue.get(field)

                if value is None or value == "":
                    empty_fields.append(field)

            if empty_fields:
                found = True

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: пустые поля: '
                    f'{", ".join(empty_fields)}'
                )

if not found:
    print("\t- Не найдено")












print("\n3 ФОРМАТНЫЕ И ТЕКСТОВЫЕ ПРОБЛЕМЫ В text")

ALLOWED_TEXT_WRAPPER_TAGS = ["<i>"]


def remove_allowed_text_tags(text):
    for opening_tag in ALLOWED_TEXT_WRAPPER_TAGS:
        tag_name = opening_tag[1:-1]
        closing_tag = f"</{tag_name}>"
        text = text.replace(opening_tag, "").replace(closing_tag, "")

    return text


found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            text = cue.get("text", "")
            text_without_allowed_tags = remove_allowed_text_tags(text)

            issues = []

            # Лишние пробелы по краям
            if text != text.strip():
                issues.append("пробелы/переносы в начале или конце")

            # Лишние пробелы возле \n
            if re.search(r"[ \t]+\n", text):
                issues.append("пробелы перед \\n")

            if re.search(r"\n[ \t]+", text):
                issues.append("пробелы после \\n")

            # Несколько пробелов или табов подряд
            if re.search(r"[ \t]{2,}", text):
                issues.append("два или более пробельных символа подряд")

            # Пробел перед знаком препинания
            if re.search(r"\s+[,.!?;:]", text):
                issues.append("пробел перед знаком препинания")

            # Нет пробела после знака препинания
            if re.search(r"[,.!?;:][А-Яа-яЁё]", text):
                issues.append("нет пробела после знака препинания")

            # Непарные кавычки
            if text.count('"') % 2 != 0:
                issues.append("непарные кавычки")

            # Латиница
            if re.search(r"[A-Za-z]", text_without_allowed_tags):
                issues.append("латиница")

            if issues:
                found = True

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: {", ".join(issues)}'
                )

                print(f'\t\t{text!r}')

if not found:
    print("\t- Не найдено")








print("\n4 НАЛИЧИЕ \\n, \\t И ПРОБЕЛОВ В name")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            name = cue.get("name", "")

            issues = []

            if "\n" in name:
                issues.append(r"\n")

            if "\t" in name:
                issues.append(r"\t")

            if name != name.strip():
                issues.append("пробел в начале/конце")

            if re.search(r" {2,}", name):
                issues.append("два или более пробелов подряд")

            if issues:
                found = True

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: name={repr(name)} '
                    f'содержит {", ".join(issues)}'
                )

if not found:
    print("\t- Не найдено")











print("\n5 НЕДОПУСТИМЫЕ СИМВОЛЫ В name")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            name = cue.get("name", "")

            if name == "???" or name == "Робот?":
                continue

            if "\n" in name or "\t" in name:
                continue

            bad_chars = sorted(set(re.findall(r"[^А-Яа-яЁё ]", name)))

            if bad_chars:
                found = True

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: name={repr(name)} '
                    f'содержит символы: '
                    f'{", ".join(repr(c) for c in bad_chars)}'
                )

if not found:
    print("\t- Не найдено")








print("\n6 ПРОВЕРКА position")

found = False

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        character_positions = {}
        dialog_characters = {}

        for cue_index, cue in enumerate(dialog, start=1):
            name = cue.get("name")
            character = cue.get("character")
            position = cue.get("position")

            if name == "Алёнка" and position != "LEFT":
                found = True
                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: Алёнка имеет position={position}, '
                    f'ожидается LEFT'
                )

            if character not in character_positions:
                character_positions[character] = position
            elif character_positions[character] != position:
                found = True
                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}: персонаж {character} '
                    f'сменил сторону {character_positions[character]} -> {position}'
                )

            dialog_characters.setdefault(character, set()).add(position)

        if len(dialog_characters) > 1:
            all_positions = set()

            for positions in dialog_characters.values():
                all_positions.update(positions)

            if len(all_positions) == 1:
                found = True

                only_position = next(iter(all_positions))

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}: '
                    f'все персонажи стоят на одной стороне ({only_position})'
                )

if not found:
    print("\t- Не найдено")









print("\n7 НАЛИЧИЕ ОРФОГРАФИЧЕСКИХ ОШИБОК В text (ЯНДЕКС СПЕЛЛЕР)")

found = False

spell_texts = []
spell_mapping = []
wrong_words = set()
report_lines = []

output_path = REPORTS_DIR / "yandex_errors.txt"

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):

            text = (
                cue.get("text", "")
                   .replace("\n", " ")
                   .strip()
            )

            spell_texts.append(text)

            spell_mapping.append({
                "quest_id": quest_id,
                "dialog_index": dialog_index,
                "cue_index": cue_index,
                "original_text": cue.get("text", "")
            })

BATCH_SIZE = 100

for start in range(0, len(spell_texts), BATCH_SIZE):
    batch_texts = spell_texts[start:start + BATCH_SIZE]
    batch_mapping = spell_mapping[start:start + BATCH_SIZE]

    response = requests.post(
        "https://speller.yandex.net/services/spellservice.json/checkTexts",
        data={
            "text": batch_texts,
            "lang": "ru",
            "format": "plain",
        },
        timeout=30
    )

    response.raise_for_status()

    spell_results = response.json()

    for info, errors in zip(batch_mapping, spell_results):
        errors = [
            error for error in errors
            if error.get("word", "").casefold() not in text_exceptions
            and not is_speller_false_positive(error)
        ]

        if not errors:
            continue

        found = True

        report_lines.append(
            f'\n\t- Квест {quest_numbers[info["quest_id"]]} (id={info["quest_id"]}), '
            f'диалог {info["dialog_index"]}, '
            f'реплика {info["cue_index"]}'
        )

        report_lines.append(f'\t\t{info["original_text"]!r}')

        for error in errors:
            word = error.get("word")
            suggestions = error.get("s", [])

            if word:
                wrong_words.add(word)

            if suggestions:
                report_lines.append(f'\t\t{word} -> {", ".join(suggestions)}')
            else:
                report_lines.append(f'\t\t{word} -> нет подсказок')

if not found:
    print("\t- Не найдено")
    report_lines.append("\t- Не найдено")
else:
    sorted_wrong_words = sorted(wrong_words, key=str.casefold)

    print("\n\tСлова, которые можно добавить в spell_exceptions.json:")

    for word in sorted_wrong_words:
        print(
            f"\t    {json.dumps(word, ensure_ascii=False)},"
        )

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n\tПолный отчёт сохранён: {output_path}")



print("\n8 НАЛИЧИЕ 'Е' ВМЕСТО 'Ё' В name И text (ПРОГОН ЧЕРЕЗ ЁТИФИКАТОР)")

found = False

yo_dictionary = load_yo_dictionary(DATA_DIR / "yo.dat")

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):

            name = cue.get("name", "")
            yoficated_name = yoficate_text(name, yo_dictionary)

            if name != yoficated_name:
                found = True

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}, name: '
                    f'"{name}" -> "{yoficated_name}"'
                )

            text = cue.get("text", "")
            yoficated_text = yoficate_text(text, yo_dictionary)

            if text != yoficated_text:
                found = True

                print(
                    f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                    f'реплика {cue_index}, text:'
                )

                print(f'\t\t{text!r}')
                print(f'\t\t↓')
                print(f'\t\t{yoficated_text!r}')

if not found:
    print("\t- Не найдено")







from dialogue_checker.alena_skins import (
    ALENA_SKINS,
    get_expected_alena_skin_sequence,
)

print("\n12 ПРОВЕРКА ПОРЯДКА СКИНОВ АЛЁНКИ В character (ДИАЛОГИ)")

found = False

expected_sequence = get_expected_alena_skin_sequence(n)

if expected_sequence is None:
    found = True
    print(f"\t- Для локации {n} не задан порядок скинов Алёнки")
else:
    known_skins = set(ALENA_SKINS.values())
    actual_sequence = []
    transitions = []

    for cutscene in all_cutscenes:
        quest_id = cutscene["id"]

        for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
            for cue_index, cue in enumerate(dialog, start=1):

                character = cue.get("character", "")

                if not character.startswith("@character/alena"):
                    continue

                if character not in known_skins:
                    found = True
                    print(
                        f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                        f'реплика {cue_index}: неизвестный скин Алёнки '
                        f'character="{character}"'
                    )
                    continue

                if not actual_sequence or actual_sequence[-1] != character:
                    actual_sequence.append(character)
                    transitions.append({
                        "quest_id": quest_id,
                        "dialog_index": dialog_index,
                        "cue_index": cue_index,
                        "character": character,
                    })

    actual_sequence = tuple(actual_sequence)

    if actual_sequence != expected_sequence:
        found = True

        expected_text = " → ".join(expected_sequence)
        actual_text = " → ".join(actual_sequence) or "скины не встретились"

        print("\t- Нарушен порядок скинов Алёнки")
        print(f"\t\tОжидался: {expected_text}")
        print(f"\t\tПолучен:  {actual_text}")

        if transitions:
            print("\t\tСмена скинов:")

            for transition in transitions:
                quest_id = transition["quest_id"]
                print(
                    f'\t\t- Квест {quest_numbers[quest_id]} (id={quest_id}), '
                    f'диалог {transition["dialog_index"]}, '
                    f'реплика {transition["cue_index"]}: '
                    f'{transition["character"]}'
                )

if not found:
    print("\t- Не найдено")







print("\n13 НЕСООТВЕТСТВИЕ name, character И emotion")

UNKNOWN_NAME = "???"

def get_character_prefix(character):
    if not character.startswith("@character/"):
        return None

    character_id = character.replace("@character/", "")

    # Алёнка имеет несколько скинов
    if character_id.startswith("alena_"):
        return "alena"

    # Иванушка может быть человеком и козлёнком
    if character_id.startswith("kozlenok_"):
        return "kozlenok"

    return character_id.split("_")[0]


def get_emotion_prefix(emotion):
    if not emotion:
        return None

    if "_" not in emotion:
        return emotion

    return emotion.rsplit("_", 1)[0]


def prefixes_match(left, right):
    return (
        left == right
        or left.startswith(f"{right}_")
        or right.startswith(f"{left}_")
    )


found = False

unknown_names = {}

for cutscene in all_cutscenes:
    for dialog in cutscene["dialogs"]:
        for cue in dialog:
            name = cue.get("name", "")
            if name == UNKNOWN_NAME:
                continue

            if name not in NAME_TO_PREFIX:
                unknown_names.setdefault(name, []).append(
                {
                    "cutscene": cutscene.get("id"),
                    "character": cue.get("character"),
                    "emotion": cue.get("emotion"),
                    "text": cue.get("text"),
                }
            )

if unknown_names:
    found = True
    new_candidates = {}

    print("\tНет соответствия для следующих name:")

    for name, entries in sorted(unknown_names.items()):
        characters = sorted({
            entry["character"]
            for entry in entries
            if entry["character"]
        })
        emotions = sorted({
            entry["emotion"]
            for entry in entries
            if entry["emotion"]
        })
        prefixes = {
            get_emotion_prefix(emotion)
            for emotion in emotions
        }
        prefixes.discard(None)

        if not prefixes:
            prefixes = {
                get_character_prefix(character)
                for character in characters
            }
            prefixes.discard(None)

        suggested_prefix = next(iter(prefixes)) if len(prefixes) == 1 else None

        if suggested_prefix is not None:
            json_name = json.dumps(name, ensure_ascii=False)
            json_prefix = json.dumps(suggested_prefix, ensure_ascii=False)
            print(f"\t{json_name}: {json_prefix},")
        else:
            print(f'\t"{name}": null,')
            print(
                "\t\tПрефикс не определён однозначно; "
                f'characters: {", ".join(characters) or "не указаны"}'
            )

        new_candidates[name] = {
            "suggested_prefix": suggested_prefix,
            "characters": characters,
            "emotions": emotions,
        }

    if UNKNOWN_CHARACTER_NAMES_PATH.exists():
        with open(UNKNOWN_CHARACTER_NAMES_PATH, "r", encoding="utf-8") as f:
            saved_candidates = json.load(f)
    else:
        saved_candidates = {}

    saved_candidates.update(new_candidates)

    with open(UNKNOWN_CHARACTER_NAMES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            saved_candidates,
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        f.write("\n")

    print(f"\n\tКандидаты сохранены в {UNKNOWN_CHARACTER_NAMES_PATH}")

else:
    for cutscene in all_cutscenes:
        quest_id = cutscene["id"]

        for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
            for cue_index, cue in enumerate(dialog, start=1):

                name = cue.get("name", "")
                character = cue.get("character", "")
                emotion = cue.get("emotion", "")

                name_prefix = None if name == UNKNOWN_NAME else NAME_TO_PREFIX.get(name)
                character_prefix = get_character_prefix(character)
                emotion_prefix = get_emotion_prefix(emotion)

                issues = []

                if character_prefix is None:
                    issues.append(f'не удалось разобрать character="{character}"')

                if emotion_prefix is None:
                    issues.append(f'не удалось разобрать emotion="{emotion}"')

                if name_prefix is not None and character_prefix is not None and not prefixes_match(name_prefix, character_prefix):
                    issues.append(f'name/character: {name_prefix} != {character_prefix}')

                if name_prefix is not None and emotion_prefix is not None and not prefixes_match(name_prefix, emotion_prefix):
                    issues.append(f'name/emotion: {name_prefix} != {emotion_prefix}')

                if character_prefix is not None and emotion_prefix is not None and not prefixes_match(character_prefix, emotion_prefix):
                    issues.append(f'character/emotion: {character_prefix} != {emotion_prefix}')

                if issues:
                    found = True

                    print(
                        f'\t- Квест {quest_numbers[quest_id]} (id={quest_id}), диалог {dialog_index}, '
                        f'реплика {cue_index}: {", ".join(issues)}'
                    )

                    print(f'\t\tname="{name}" -> {name_prefix}')
                    print(f'\t\tcharacter="{character}" -> {character_prefix}')
                    print(f'\t\temotion="{emotion}" -> {emotion_prefix}')

if not found:
    print("\t- Не найдено")







print("\nN РУЧНАЯ ПРОВЕРКА: ПРОВЕРКА МЫСЛЕЙ")

thought_lines = []

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]
    local_quest_number = quest_numbers[quest_id]
    has_thought = any(
        cue.get("cue_type") == "THOUGHT_BUBBLE"
        for dialog in cutscene["dialogs"]
        for cue in dialog
    )

    if not has_thought:
        continue

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            text = cue.get("text", "").replace("\n", " ")

            if cue.get("cue_type") == "THOUGHT_BUBBLE":
                text = f"(МЫСЛЬ) {text}"

            thought_lines.append(
                f"[{local_quest_number}:{dialog_index}:{cue_index}] {text}"
            )

thoughts_path = REPORTS_DIR / "cutscenes_thoughts_for_review.txt"

if thought_lines:
    with open(thoughts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(thought_lines))
        f.write("\n")

    print(
        f"\tСохранено: {thoughts_path}, "
        "проверяй оформление мыслей через нейронку"
    )
else:
    print("\t- Мысли не найдены, файл не сформирован")







print("\nN РУЧНАЯ ПРОВЕРКА: ПРОВЕРКА НА ПУНКТУАЦИЮ ВСЕХ text")

review_lines = []

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]
    local_quest_number = quest_numbers[quest_id]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            text = cue.get("text", "").replace("\n", " ")
            review_lines.append(
                f"[{local_quest_number}:{dialog_index}:{cue_index}] {text}"
            )

review_path = REPORTS_DIR / "cutscenes_texts_for_review.txt"

with open(review_path, "w", encoding="utf-8") as f:
    f.write("\n".join(review_lines))
    f.write("\n")

print(
    f"\tСохранён единый компактный файл: {review_path} "
    f"({len(review_lines)} реплик)"
)








print("\nN РУЧНАЯ ПРОВЕРКА: text С ПЕРСОНАЖЕМ И ЭМОЦИЕЙ")


def suggest_emotion_description(emotion):
    if not emotion or "_" not in emotion:
        return ""

    emotion_suffix = emotion.rsplit("_", 1)[-1]
    descriptions = [
        description
        for known_emotion, description in EMOTION_DESCRIPTIONS.items()
        if known_emotion.rsplit("_", 1)[-1] == emotion_suffix
        and description
    ]

    if not descriptions:
        return ""

    unique_descriptions = sorted(set(descriptions))
    return max(
        unique_descriptions,
        key=lambda description: descriptions.count(description),
    )


emotion_review_lines = []
missing_emotions = set()

for cutscene in all_cutscenes:
    quest_id = cutscene["id"]
    local_quest_number = quest_numbers[quest_id]

    for dialog_index, dialog in enumerate(cutscene["dialogs"], start=1):
        for cue_index, cue in enumerate(dialog, start=1):
            name = cue.get("name", "")
            emotion = cue.get("emotion", "")
            text = cue.get("text", "").replace("\n", " ")
            emotion_description = EMOTION_DESCRIPTIONS.get(emotion)

            if emotion_description is None:
                missing_emotions.add(emotion)
                emotion_with_description = emotion
            else:
                emotion_with_description = f"{emotion} — {emotion_description}"

            emotion_review_lines.append(
                f"[{local_quest_number}:{dialog_index}:{cue_index}] "
                f"{name} || {emotion_with_description} || {text}"
            )

emotion_review_path = REPORTS_DIR / "cutscenes_emotions_for_review.txt"

if missing_emotions:
    print("\t- Нет описания для emotion:")
    for emotion in sorted(missing_emotions):
        suggested_description = suggest_emotion_description(emotion)
        json_emotion = json.dumps(emotion, ensure_ascii=False)
        json_description = json.dumps(
            suggested_description,
            ensure_ascii=False,
        )
        print(f"\t\t{json_emotion}: {json_description},")

    print(
        "\tФайл для проверки не сформирован. "
        "Добавь описания эмоций и запусти анализатор повторно."
    )
else:
    with open(emotion_review_path, "w", encoding="utf-8") as f:
        f.write("\n".join(emotion_review_lines))
        f.write("\n")

    print(
        f"\tСохранено: {emotion_review_path}, "
        f"проверяй через нейронку на соответствие эмоции и реплики"
    )

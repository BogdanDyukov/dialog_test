import json
from pathlib import Path
from pymorphy3 import MorphAnalyzer

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

morph = MorphAnalyzer()


def get_forms(entry):
    # Не склонять
    if entry["gender"] is None and entry["number"] is None:
        return {entry["word"].lower()}

    wanted = {"NOUN", "nomn"}

    if entry["gender"] is not None:
        wanted.add(entry["gender"])

    if entry["number"] is not None:
        wanted.add(entry["number"])

    for parse in morph.parse(entry["word"]):
        if wanted.issubset(parse.tag.grammemes):
            return {form.word.lower() for form in parse.lexeme}

    return {entry["word"].lower()}


def build_spell_exceptions(entries):
    result = set()

    for entry in entries:
        result.update(get_forms(entry))

    return result


def is_speller_false_positive(error):
    word = error.get("word", "")
    suggestions = error.get("s", [])

    if not isinstance(word, str) or not isinstance(suggestions, list):
        return False

    normalized_word = word.casefold()

    return any(
        isinstance(suggestion, str)
        and suggestion.casefold() == normalized_word
        for suggestion in suggestions
    )


with open(DATA_DIR / "spell_exceptions.json", "r", encoding="utf-8") as f:
    spell_exceptions = json.load(f)

common_exceptions = build_spell_exceptions(
    spell_exceptions.get("common", [])
)

title_exceptions = common_exceptions | build_spell_exceptions(
    spell_exceptions.get("title", [])
)

text_exceptions = common_exceptions | build_spell_exceptions(
    spell_exceptions.get("text", [])
)

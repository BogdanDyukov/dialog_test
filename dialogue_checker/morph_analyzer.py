import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def normalize_spell_exceptions(entries):
    return {
        entry.casefold()
        for entry in entries
        if isinstance(entry, str)
    }


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

common_exceptions = normalize_spell_exceptions(
    spell_exceptions.get("common", [])
)

title_exceptions = common_exceptions | normalize_spell_exceptions(
    spell_exceptions.get("title", [])
)

text_exceptions = common_exceptions | normalize_spell_exceptions(
    spell_exceptions.get("text", [])
)

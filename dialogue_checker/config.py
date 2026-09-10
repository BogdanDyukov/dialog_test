import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config.json"


def _get_path(config, key):
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'В {CONFIG_PATH} не указан путь "{key}"')

    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError(f'Путь "{key}" в {CONFIG_PATH} должен быть абсолютным')

    return path.resolve()


def load_project_paths():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"Не найден конфиг: {CONFIG_PATH}")
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Ошибка в {CONFIG_PATH}: {error}")

    return {
        "quest_titles_dir": _get_path(config, "quest_titles_dir"),
        "cutscenes_dir": _get_path(config, "cutscenes_dir"),
    }

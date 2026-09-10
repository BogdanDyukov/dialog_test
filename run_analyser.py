from pathlib import Path
import json
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
REPORTS_DIR = PROJECT_ROOT / "reports"

ANALYZERS = {
    "1": [("Названия квестов и реварды", PROJECT_ROOT / "analyzers" / "quest_analyser.py")],
    "2": [("Диалоги катсцен", PROJECT_ROOT / "analyzers" / "cutscenes_analyser.py")],
    "3": [
        ("Названия квестов и реварды", PROJECT_ROOT / "analyzers" / "quest_analyser.py"),
        ("Диалоги катсцен", PROJECT_ROOT / "analyzers" / "cutscenes_analyser.py"),
    ],
}


def ensure_config_exists():
    if CONFIG_PATH.exists():
        return True

    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {
                "quest_titles_dir": "",
                "cutscenes_dir": "",
            },
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")

    print(f"Создан конфиг: {CONFIG_PATH}")
    print("Заполните конфиг и запустите анализатор снова.")
    return False


def ask_test_type():
    print("Что тестируем?")
    print("1 — названия квестов")
    print("2 — диалоги")
    print("3 — всё")

    choice = input("\nВыбор: ").strip()
    if choice not in ANALYZERS:
        print(f"Неизвестный вариант: {choice}")
        raise SystemExit(2)

    return ANALYZERS[choice]


def ask_location_number():
    value = input("Номер локации: ").strip()

    try:
        location_number = int(value)
    except ValueError:
        print(f"Некорректный номер локации: {value}")
        raise SystemExit(2)

    if location_number < 1:
        print("Номер локации должен быть больше нуля")
        raise SystemExit(2)

    return location_number


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not ensure_config_exists():
        return 1

    analyzers = ask_test_type()
    location_number = ask_location_number()
    exit_code = 0

    for title, script_path in analyzers:
        print(f"\n{'=' * 10} {title} {'=' * 10}", flush=True)
        result = subprocess.run(
            [sys.executable, str(script_path), str(location_number)],
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            exit_code = result.returncode

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

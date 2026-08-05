import requests

text = """Мистер а как тибя, зовут?"""

response = requests.post(
    "https://api.languagetool.org/v2/check",
    data={
        "text": text,
        "language": "ru-RU",
    },
    timeout=30
)

response.raise_for_status()

result = response.json()

for match in result.get("matches", []):
    word = text[
        match["offset"]:match["offset"] + match["length"]
    ]

    print("Слово:", word)
    print("Правило:", match["rule"]["id"])
    print("Категория:", match["rule"]["category"]["name"])
    print("Сообщение:", match["message"])
    print()
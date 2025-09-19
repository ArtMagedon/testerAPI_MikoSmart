import json

default_fonts = {
    "label": {"family": "Arial", "size": 10, "weight": "bold"},
    "combo": {"family": "Arial", "size": 10, "weight": "bold"},
    "entry": {"family": "Consolas", "size": 10},
    "button": {"family": "Arial", "size": 10},
    "body": {"family": "Consolas", "size": 10},
    "output": {"family": "Consolas", "size": 10}
}


def create_json_file(n: int = 20, filename: str = "file.json"):
    data = {"top": "",
            "fonts": default_fonts,
            "blocks": []}
    for i in range(1, n + 1):
        temp = {"label": f"№{i}",
            "Method": "GET",
            "entry": "",
            "body": ""
        }
        data["blocks"].append(temp)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


create_json_file()

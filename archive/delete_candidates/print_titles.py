import json

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent

with open(str(PROJECT_ROOT / "maps/maps_output.json"), 'r', encoding='utf-8') as f:
    maps = json.load(f)
    for m in maps[100:125]:
        print(f"- {m['task_title']}")

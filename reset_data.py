"""Reset local JSON-backed user and report data.

Run manually from the server directory only when a full application-data reset
is intended: `python reset_data.py`.
"""

import json
from pathlib import Path


DATA_FILES = ("users.json", "user_reports.json", "reports.json")
APP_DIRECTORY = Path(__file__).resolve().parent / "app"


def main():
    for filename in DATA_FILES:
        path = APP_DIRECTORY / filename
        path.write_text(json.dumps({}, indent=2) + "\n", encoding="utf-8")
        print(f"Cleared {path.name}")


if __name__ == "__main__":
    main()

from pathlib import Path
import json


def read_file(file_name: str) -> list[dict]:
    file_path = str(Path(__file__).parent.parent / "data" / file_name)
    with open(file_path, mode="r") as f:
        contents = f.read()
    return json.loads(contents)

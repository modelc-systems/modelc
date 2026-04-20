from __future__ import annotations

import json
import tarfile
import tempfile
from pathlib import Path
from typing import Any


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json_input(input_value: str | None = None, input_file: Path | None = None) -> dict[str, Any]:
    if input_value and input_file:
        raise ValueError("Use either --input or --input-file, not both")

    if input_value:
        return json.loads(input_value)

    if input_file:
        return json.loads(input_file.read_text(encoding="utf-8"))

    import sys
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            return json.loads(raw)

    return {}


def write_json_stdout(data: dict[str, Any]) -> None:
    import sys
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")


def create_tar_gz(source_dir: Path, output_file: Path) -> None:
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=".")


def extract_tar_gz(archive_path: Path) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="modelc-run-"))
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=temp_dir)
    return temp_dir

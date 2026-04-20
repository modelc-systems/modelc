from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

from modelc.exceptions import ExecutionError, ManifestValidationError
from modelc.io_utils import extract_tar_gz
from modelc.manifest import find_manifest, load_manifest
from modelc.models import ModelManifest


def materialize_target(target: Path) -> tuple[Path, ModelManifest]:
    if target.is_file() and target.name.endswith(".modelc.tar.gz"):
        workspace = extract_tar_gz(target)
        manifest_path = find_manifest(workspace)
        manifest = load_manifest(manifest_path)
        return workspace, manifest

    if target.is_dir():
        manifest_path = find_manifest(target)
        manifest = load_manifest(manifest_path)
        return target, manifest

    raise ManifestValidationError(f"Unsupported run target: {target}")


def execute_entrypoint(workspace: Path, manifest: ModelManifest, payload: dict) -> dict:
    command = manifest.entrypoint.command
    parts = shlex.split(command)

    if not parts:
        raise ExecutionError("Entrypoint command is empty")

    if parts[0] == "python":
        parts[0] = sys.executable

    result = subprocess.run(
        parts,
        cwd=workspace,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        raise ExecutionError(
            "Entrypoint execution failed\n"
            f"Command: {command}\n"
            f"Exit code: {result.returncode}\n"
            f"stderr:\n{result.stderr.strip()}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ExecutionError(
            f"Entrypoint did not return valid JSON on stdout. Raw stdout:\n{result.stdout}"
        ) from exc

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from modelc.exceptions import ManifestValidationError
from modelc.models import ModelManifest


def load_manifest(path: Path) -> ModelManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestValidationError(f"Manifest not found: {path}") from exc
    except Exception as exc:
        raise ManifestValidationError(f"Failed to read manifest: {exc}") from exc

    if not isinstance(raw, dict):
        raise ManifestValidationError("Manifest must be a YAML object")

    try:
        return ModelManifest.model_validate(raw)
    except ValidationError as exc:
        raise ManifestValidationError(str(exc)) from exc


def find_manifest(target: Path) -> Path:
    if target.is_file() and target.name in {"model.yaml", "manifest.yaml"}:
        return target
    candidate = target / "model.yaml"
    if candidate.exists():
        return candidate
    candidate = target / "manifest.yaml"
    if candidate.exists():
        return candidate
    raise ManifestValidationError(f"No model.yaml or manifest.yaml found in {target}")


def dump_manifest_data(manifest: ModelManifest) -> str:
    return yaml.safe_dump(manifest.model_dump(mode="python"), sort_keys=False)


def validate_project_paths(project_root: Path, manifest: ModelManifest) -> None:
    for artifact_name, artifact in manifest.artifacts.items():
        artifact_path = (project_root / artifact.path).resolve()
        root_resolved = project_root.resolve()
        if not str(artifact_path).startswith(str(root_resolved)):
            raise ManifestValidationError(
                f"artifacts.{artifact_name}.path points outside project root: {artifact.path}"
            )
        if not artifact_path.exists():
            raise ManifestValidationError(
                f"artifacts.{artifact_name}.path does not exist: {artifact.path}"
            )

    command = manifest.entrypoint.command.strip()
    parts = command.split()
    if len(parts) < 2:
        raise ManifestValidationError(
            "entrypoint.command must follow a simple pattern like 'python run.py'"
        )
    entrypoint_path = (project_root / parts[-1]).resolve()
    if not str(entrypoint_path).startswith(str(project_root.resolve())):
        raise ManifestValidationError("entrypoint path points outside project root")
    if not entrypoint_path.exists():
        raise ManifestValidationError(f"Entrypoint file does not exist: {parts[-1]}")

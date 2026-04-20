from __future__ import annotations

from pathlib import Path

from modelc.manifest import find_manifest, load_manifest


def inspect_target(target: Path) -> str:
    manifest_path = find_manifest(target)
    manifest = load_manifest(manifest_path)

    lines: list[str] = []
    lines.append(f"Name: {manifest.metadata.name}")
    lines.append(f"Version: {manifest.metadata.version}")
    lines.append(f"API Version: {manifest.apiVersion}")
    lines.append(f"Runtime: {manifest.runtime.type} {manifest.runtime.version}")
    lines.append(f"Entrypoint: {manifest.entrypoint.command}")
    lines.append("")
    lines.append("Artifacts:")
    for name, artifact in manifest.artifacts.items():
        lines.append(f"  - {name}: {artifact.path} ({artifact.format})")
    lines.append("")
    lines.append("Input:")
    lines.append(f"  type: {manifest.interface.input.type}")
    for key, value in manifest.interface.input.schema.items():
        lines.append(f"    {key}: {value}")
    lines.append("")
    lines.append("Output:")
    lines.append(f"  type: {manifest.interface.output.type}")
    for key, value in manifest.interface.output.schema.items():
        lines.append(f"    {key}: {value}")

    return "\n".join(lines)

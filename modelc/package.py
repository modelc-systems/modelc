from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from modelc.io_utils import create_tar_gz, ensure_dir
from modelc.manifest import dump_manifest_data, validate_project_paths
from modelc.models import ModelManifest


def build_package(project_root: Path, manifest: ModelManifest) -> Path:
    validate_project_paths(project_root, manifest)

    dist_dir = project_root / "dist"
    ensure_dir(dist_dir)

    build_root = project_root / ".modelc-build"
    if build_root.exists():
        shutil.rmtree(build_root)

    ensure_dir(build_root / "entrypoint")
    ensure_dir(build_root / "artifacts")
    ensure_dir(build_root / "metadata")

    # Write resolved manifest
    manifest_copy = manifest.model_copy(deep=True)

    # Copy artifacts into packaged layout and rewrite paths
    for name, artifact in manifest_copy.artifacts.items():
        src = (project_root / artifact.path).resolve()
        dest = build_root / "artifacts" / name
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            ensure_dir(dest.parent)
            shutil.copy2(src, dest)
        artifact.path = f"artifacts/{name}"

    # Copy entrypoint and rewrite command
    command_parts = manifest.entrypoint.command.split()
    interpreter = command_parts[0]
    source_script = command_parts[-1]
    src_entrypoint = (project_root / source_script).resolve()
    dest_entrypoint = build_root / "entrypoint" / Path(source_script).name
    shutil.copy2(src_entrypoint, dest_entrypoint)
    manifest_copy.entrypoint.command = f"{interpreter} entrypoint/{Path(source_script).name}"

    (build_root / "manifest.yaml").write_text(dump_manifest_data(manifest_copy), encoding="utf-8")

    build_meta = {
        "tool": "modelc",
        "toolVersion": "0.1.0",
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "packageFormat": "modelc/v0",
        "sourceManifest": "model.yaml",
    }
    (build_root / "metadata" / "build.json").write_text(
        json.dumps(build_meta, indent=2),
        encoding="utf-8",
    )

    output_path = dist_dir / f"{manifest.metadata.name}-{manifest.metadata.version}.modelc.tar.gz"
    create_tar_gz(build_root, output_path)
    shutil.rmtree(build_root)
    return output_path

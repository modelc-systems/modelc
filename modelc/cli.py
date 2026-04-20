from __future__ import annotations

from pathlib import Path
import sys

import typer

from modelc.exceptions import (
    ExecutionError,
    InputValidationError,
    ManifestValidationError,
    ModelcError,
    OutputValidationError,
)
from modelc.inspectors import inspect_target
from modelc.io_utils import load_json_input, write_json_stdout
from modelc.manifest import find_manifest, load_manifest
from modelc.package import build_package
from modelc.runtime import execute_entrypoint, materialize_target
from modelc.schema import validate_input_payload, validate_output_payload

app = typer.Typer(no_args_is_help=True, help="CLI for portable, inspectable AI model containers.")


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, ManifestValidationError):
        typer.secho(f"Manifest error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)
    if isinstance(exc, InputValidationError):
        typer.secho(f"Input error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=3)
    if isinstance(exc, ExecutionError):
        typer.secho(f"Execution error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=4)
    if isinstance(exc, OutputValidationError):
        typer.secho(f"Output error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=5)

    typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


@app.command()
def build(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True)
) -> None:
    """Build a model container from a project directory."""
    try:
        manifest_path = find_manifest(path)
        manifest = load_manifest(manifest_path)
        output_path = build_package(path, manifest)
        typer.echo("Built model container:")
        typer.echo(f"  Name: {manifest.metadata.name}")
        typer.echo(f"  Version: {manifest.metadata.version}")
        typer.echo(f"  Package: {output_path}")
    except Exception as exc:
        _handle_error(exc)


@app.command()
def inspect(
    path: Path = typer.Argument(Path("."), exists=True, resolve_path=True)
) -> None:
    """Inspect a local project directory."""
    try:
        if path.is_file() and path.name.endswith(".modelc.tar.gz"):
            from modelc.io_utils import extract_tar_gz
            path = extract_tar_gz(path)
        typer.echo(inspect_target(path))
    except Exception as exc:
        _handle_error(exc)


@app.command()
def run(
    target: Path = typer.Argument(Path("."), exists=True, resolve_path=True),
    input: str | None = typer.Option(None, "--input", help="Inline JSON input payload."),
    input_file: Path | None = typer.Option(None, "--input-file", exists=True, resolve_path=True, help="Path to JSON input file."),
) -> None:
    """Run a local project or packaged model container."""
    try:
        payload = load_json_input(input_value=input, input_file=input_file)
        workspace, manifest = materialize_target(target)

        validate_input_payload(payload, manifest.interface.input.schema)
        output = execute_entrypoint(workspace, manifest, payload)
        validate_output_payload(output, manifest.interface.output.schema)

        write_json_stdout(output)
    except Exception as exc:
        _handle_error(exc)


if __name__ == "__main__":
    app()

from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


ALLOWED_SCHEMA_TYPES = {"string", "float", "int", "boolean"}


class Metadata(BaseModel):
    name: str
    version: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("metadata.name must be non-empty")
        return v


class Runtime(BaseModel):
    type: Literal["python"]
    version: str
    dependencies: List[str] = Field(default_factory=list)


class ArtifactDefinition(BaseModel):
    path: str
    format: str


class InterfaceSpec(BaseModel):
    type: str
    schema: Dict[str, str]

    @field_validator("schema")
    @classmethod
    def validate_schema(cls, value: Dict[str, str]) -> Dict[str, str]:
        if not isinstance(value, dict) or not value:
            raise ValueError("schema must be a non-empty object")
        for key, type_name in value.items():
            if type_name not in ALLOWED_SCHEMA_TYPES:
                raise ValueError(
                    f"schema field '{key}' has unsupported type '{type_name}'. "
                    f"Allowed types: {sorted(ALLOWED_SCHEMA_TYPES)}"
                )
        return value


class Interface(BaseModel):
    input: InterfaceSpec
    output: InterfaceSpec


class Entrypoint(BaseModel):
    command: str

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("entrypoint.command must be non-empty")
        return v


class ModelManifest(BaseModel):
    apiVersion: Literal["modelc.dev/v0"]
    kind: Literal["ModelContainer"]
    metadata: Metadata
    runtime: Runtime
    artifacts: Dict[str, ArtifactDefinition]
    interface: Interface
    entrypoint: Entrypoint
    contracts: List[str] = Field(default_factory=list)

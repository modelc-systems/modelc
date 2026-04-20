from __future__ import annotations

from typing import Any

from modelc.exceptions import InputValidationError, OutputValidationError


TYPE_MAP = {
    "string": str,
    "float": (float, int),
    "int": int,
    "boolean": bool,
}


def _validate_payload(payload: dict[str, Any], schema: dict[str, str], error_cls: type[Exception], kind: str) -> None:
    if not isinstance(payload, dict):
        raise error_cls(f"{kind} payload must be a JSON object")

    for field_name, type_name in schema.items():
        if field_name not in payload:
            raise error_cls(f"{kind}.{field_name} is required")
        expected = TYPE_MAP[type_name]
        value = payload[field_name]
        if not isinstance(value, expected) or (type_name == "boolean" and type(value) is not bool):
            raise error_cls(f"{kind}.{field_name} must be of type {type_name}")


def validate_input_payload(payload: dict[str, Any], schema: dict[str, str]) -> None:
    _validate_payload(payload, schema, InputValidationError, "input")


def validate_output_payload(payload: dict[str, Any], schema: dict[str, str]) -> None:
    _validate_payload(payload, schema, OutputValidationError, "output")

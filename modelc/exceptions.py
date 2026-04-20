class ModelcError(Exception):
    """Base exception for modelc."""


class ManifestValidationError(ModelcError):
    """Raised when the manifest is invalid."""


class InputValidationError(ModelcError):
    """Raised when runtime input is invalid."""


class OutputValidationError(ModelcError):
    """Raised when runtime output is invalid."""


class ExecutionError(ModelcError):
    """Raised when entrypoint execution fails."""

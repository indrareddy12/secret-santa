"""Custom exceptions for the Secret Santa application."""


class SecretSantaError(Exception):
    """Base class for all application-specific errors."""


class InvalidInputError(SecretSantaError):
    """Raised when input data (CSV rows, files, etc.) is malformed or invalid."""


class FileParsingError(SecretSantaError):
    """Raised when a file cannot be read or parsed."""


class AssignmentError(SecretSantaError):
    """Raised when a valid Secret Santa assignment cannot be produced."""


class InsufficientEmployeesError(AssignmentError):
    """Raised when there are not enough employees to form valid assignments."""

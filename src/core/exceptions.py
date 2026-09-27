"""
MindPulse: Custom Exception Hierarchy
"""


class MindPulseException(Exception):
    """Base exception for all domain-specific errors in MindPulse."""
    pass


class AuthenticationError(MindPulseException):
    """Raised when authentication or authorization fails."""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """Raised when attempting to register a username that already exists."""
    pass


class ValidationError(MindPulseException):
    """Raised when user input violates validation bounds or rules."""
    pass


class StorageError(MindPulseException):
    """Raised when database or file I/O operations fail."""
    pass


class AssessmentNotFoundError(MindPulseException):
    """Raised when an unrecognized assessment type is queried."""
    pass

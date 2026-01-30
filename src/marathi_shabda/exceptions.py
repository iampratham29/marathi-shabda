"""Custom exceptions for marathi-pratham library."""


class MarathiShabdaError(Exception):
    """Base exception for all marathi-shabda errors."""
    pass


class DatabaseError(MarathiShabdaError):
    """Raised when database operations fail."""
    pass


class NormalizationError(MarathiShabdaError):
    """Raised when input normalization fails."""
    pass


class InvalidInputError(MarathiShabdaError):
    """Raised when input validation fails."""
    pass

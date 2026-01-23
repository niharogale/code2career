# autodoc/core/exceptions.py
"""
Custom exception classes for autodoc.

This module defines a hierarchy of exceptions to provide better error handling
and more informative error messages throughout the autodoc application.
"""


class AutodocError(Exception):
    """
    Base exception class for all autodoc-related errors.
    
    All custom exceptions in autodoc should inherit from this class,
    allowing users to catch all autodoc-specific errors with a single except clause.
    """
    pass


class NotInitializedError(AutodocError):
    """
    Raised when an autodoc operation is attempted but the .autodoc/ directory doesn't exist.
    
    This typically means the user needs to run 'autodoc init' first.
    """
    def __init__(self, path: str = None):
        if path:
            message = f"Autodoc not initialized in {path}. Run 'autodoc init' first."
        else:
            message = "Autodoc not initialized in this repository. Run 'autodoc init' first."
        super().__init__(message)


class RepositoryNotFoundError(AutodocError):
    """
    Raised when a git repository cannot be found at the specified path.
    
    This indicates that the current directory or specified path is not
    a valid git repository (no .git directory found).
    """
    def __init__(self, path: str = None):
        if path:
            message = f"{path} is not a git repository (no .git directory found)"
        else:
            message = "Not a git repository (no .git directory found)"
        super().__init__(message)


class StateCorruptedError(AutodocError):
    """
    Raised when the state.json file is invalid or corrupted.
    
    This can occur if the state file has been manually edited incorrectly
    or if there was an error during a previous write operation.
    """
    def __init__(self, details: str = None):
        if details:
            message = f"State file is corrupted or invalid: {details}"
        else:
            message = "State file is corrupted or invalid"
        super().__init__(message)


class ConfigError(AutodocError):
    """
    Raised when the config.yaml file is malformed or contains invalid values.
    
    This can occur if the configuration file has syntax errors or
    if required configuration values are missing or invalid.
    """
    def __init__(self, details: str = None):
        if details:
            message = f"Configuration error: {details}"
        else:
            message = "Configuration file is malformed or invalid"
        super().__init__(message)

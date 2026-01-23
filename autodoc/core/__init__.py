# autodoc/core/__init__.py

"""
Core module for autodoc - provides fundamental abstractions.
"""

from autodoc.core.repository import Repository, SOURCE_EXTENSIONS, IGNORE_DIRS
from autodoc.core.scan import (
    ChangeType,
    FileChange,
    ScanResult,
    compute_file_hash,
    scan_repository,
    apply_scan_to_state,
)
from autodoc.core.state import (
    default_state,
    load_state,
    remove_file,
    save_state,
    update_file,
)
from autodoc.core.config import AutodocConfig
from autodoc.core.exceptions import (
    AutodocError,
    NotInitializedError,
    RepositoryNotFoundError,
    StateCorruptedError,
    ConfigError,
)

__all__ = [
    # Repository
    "Repository",
    "SOURCE_EXTENSIONS",
    "IGNORE_DIRS",
    # Scanning
    "ChangeType",
    "FileChange",
    "ScanResult",
    "compute_file_hash",
    "scan_repository",
    "apply_scan_to_state",
    # State
    "default_state",
    "load_state",
    "remove_file",
    "save_state",
    "update_file",
    # Configuration
    "AutodocConfig",
    # Exceptions
    "AutodocError",
    "NotInitializedError",
    "RepositoryNotFoundError",
    "StateCorruptedError",
    "ConfigError",
]

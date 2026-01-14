# autodoc/core/__init__.py

"""
Core module for autodoc - provides fundamental abstractions.
"""

from autodoc.core.repository import Repository, SOURCE_EXTENSIONS, IGNORE_DIRS
from autodoc.core.scan import (
    ChangeType,
    FileChange,
    compute_file_hash,
    detect_changes,
    get_changed_files,
    scan_repository,
    summarize_changes,
)
from autodoc.core.state import (
    default_state,
    load_state,
    remove_file,
    save_state,
    update_file,
)

__all__ = [
    # Repository
    "Repository",
    "SOURCE_EXTENSIONS",
    "IGNORE_DIRS",
    # Scanning
    "ChangeType",
    "FileChange",
    "compute_file_hash",
    "detect_changes",
    "get_changed_files",
    "scan_repository",
    "summarize_changes",
    # State
    "default_state",
    "load_state",
    "remove_file",
    "save_state",
    "update_file",
]

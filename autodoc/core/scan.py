# autodoc/core/scan.py

"""
Repository scanning and change detection.

This module provides functionality to:
- Compute file hashes for content comparison
- Scan a repository for source files
- Detect changes (new, modified, deleted files) compared to previous state
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from autodoc.core.repository import Repository
from autodoc.core.state import remove_file, update_file


class ChangeType(Enum):
    """Types of file changes that can be detected."""

    NEW = "new"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


@dataclass
class FileChange:
    """
    Represents a detected change to a file.
    """

    path: str
    change_type: ChangeType
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None

    def __repr__(self) -> str:
        return f"FileChange({self.path!r}, {self.change_type.value})"


def compute_file_hash(path: Path) -> str:
    """
    Compute a stable SHA-256 hash for a file's contents.

    Args:
        path: Path to the file to hash.

    Returns:
        Hexadecimal string of the file's SHA-256 hash.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def detect_changes(
    repo: Repository,
    state: Dict[str, Any],
) -> List[FileChange]:
    """
    Detect file changes by comparing current repository state against stored state.

    Args:
        repo: Repository context to scan.
        state: Current state dictionary containing previous file information.

    Returns:
        List of FileChange objects describing all detected changes.
    """
    changes: List[FileChange] = []
    current_files = repo.get_files()

    # Convert to set of string paths for easier comparison
    current_paths = {str(f) for f in current_files}
    previous_paths = set(state.get("files", {}).keys())

    # Check for new and modified files
    for rel_path in current_files:
        path_str = str(rel_path)
        abs_path = repo.get_absolute_path(rel_path)

        try:
            current_hash = compute_file_hash(abs_path)
        except (OSError, IOError):
            # Skip files we can't read
            continue

        if path_str not in previous_paths:
            # New file
            changes.append(
                FileChange(
                    path=path_str,
                    change_type=ChangeType.NEW,
                    old_hash=None,
                    new_hash=current_hash,
                )
            )
        else:
            # Existing file - check if modified
            old_hash = state["files"][path_str].get("hash")
            if old_hash != current_hash:
                changes.append(
                    FileChange(
                        path=path_str,
                        change_type=ChangeType.MODIFIED,
                        old_hash=old_hash,
                        new_hash=current_hash,
                    )
                )
            else:
                changes.append(
                    FileChange(
                        path=path_str,
                        change_type=ChangeType.UNCHANGED,
                        old_hash=old_hash,
                        new_hash=current_hash,
                    )
                )

    # Check for deleted files
    for path_str in previous_paths:
        if path_str not in current_paths:
            old_hash = state["files"][path_str].get("hash")
            changes.append(
                FileChange(
                    path=path_str,
                    change_type=ChangeType.DELETED,
                    old_hash=old_hash,
                    new_hash=None,
                )
            )

    return changes


def scan_repository(repo: Repository, state: Dict[str, Any]) -> List[FileChange]:
    """
    Scan the repository and update state to reflect current contents.

    This function:
    1. Discovers all source files in the repository
    2. Compares against the previous state to detect changes
    3. Updates state['files'] with current file information
    4. Updates repository metadata in state['repo']

    Args:
        repo: Repository context to scan.
        state: State dictionary to update (modified in-place).

    Returns:
        List of FileChange objects describing all detected changes.
    """
    # Detect all changes
    changes = detect_changes(repo, state)

    # Current timestamp for all updates
    timestamp = datetime.now(timezone.utc).isoformat()

    # Update state based on changes
    for change in changes:
        if change.change_type == ChangeType.DELETED:
            remove_file(state, change.path)
        elif change.change_type in (ChangeType.NEW, ChangeType.MODIFIED):
            update_file(
                state,
                file_path=change.path,
                file_hash=change.new_hash,
                change_type=change.change_type.value,
                last_modified=timestamp,
            )
        # UNCHANGED files don't need state updates

    # Update repository metadata
    state["repo"] = repo.to_dict()
    state["last_scan"] = timestamp

    return changes


def get_changed_files(changes: List[FileChange]) -> List[FileChange]:
    """
    Filter a list of changes to only include actual changes (new, modified, deleted).

    Args:
        changes: List of all file changes.

    Returns:
        List containing only NEW, MODIFIED, and DELETED changes.
    """
    return [c for c in changes if c.change_type != ChangeType.UNCHANGED]


def summarize_changes(changes: List[FileChange]) -> Dict[str, int]:
    """
    Summarize changes by type.

    Args:
        changes: List of file changes.

    Returns:
        Dictionary with counts for each change type.
    """
    summary = {
        "new": 0,
        "modified": 0,
        "deleted": 0,
        "unchanged": 0,
        "total": len(changes),
    }
    for change in changes:
        summary[change.change_type.value] += 1
    return summary

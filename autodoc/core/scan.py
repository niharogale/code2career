# autodoc/core/scan.py
"""
Repository scanning module - enumerates files and computes hashes.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib

from autodoc.core.repository import Repository


class ChangeType(Enum):
    """Types of changes detected between scans."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


@dataclass
class FileChange:
    """Represents a change to a single file."""
    path: str
    change_type: ChangeType
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    language: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for state storage."""
        return {
            "hash": self.new_hash or self.old_hash or "",
            "change_type": self.change_type.value,
            "language": self.language,
            "last_modified": datetime.now(timezone.utc).isoformat()
        }


@dataclass
class ScanResult:
    """Result of a repository scan."""
    files: Dict[str, FileChange]
    added: List[str]
    modified: List[str]
    deleted: List[str]
    unchanged: List[str]
    
    @property
    def has_changes(self) -> bool:
        """Check if any changes were detected."""
        return bool(self.added or self.modified or self.deleted)
    
    @property
    def total_files(self) -> int:
        """Total number of tracked files."""
        return len(self.files)
    
    def summary(self) -> str:
        """Human-readable summary of scan results."""
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.modified:
            parts.append(f"{len(self.modified)} modified")
        if self.deleted:
            parts.append(f"{len(self.deleted)} deleted")
        if self.unchanged:
            parts.append(f"{len(self.unchanged)} unchanged")
        
        if not parts:
            return "No files found"
        return ", ".join(parts)


def compute_file_hash(path: Path) -> str:
    """
    Compute a stable SHA-256 hash for a file's contents.
    
    Args:
        path: Path to the file to hash
        
    Returns:
        Hex string of the SHA-256 hash
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_repository(repo: Repository, previous_state: Dict[str, Any]) -> ScanResult:
    """
    Scan a repository and detect changes since the last scan.
    
    Args:
        repo: Repository context
        previous_state: State dict from the previous scan (with 'files' key)
        
    Returns:
        ScanResult containing all file changes
    """
    previous_files = previous_state.get("files", {})
    current_files: Dict[str, FileChange] = {}
    
    added: List[str] = []
    modified: List[str] = []
    deleted: List[str] = []
    unchanged: List[str] = []
    
    # Get all source files from the repository
    source_files = repo.get_source_files()
    current_paths = set()
    
    # Process each current file
    for file_path in source_files:
        rel_path = repo.get_relative_path(file_path)
        current_paths.add(rel_path)
        
        try:
            new_hash = compute_file_hash(file_path)
        except (IOError, OSError):
            # Skip files we can't read
            continue
        
        language = repo.get_language(file_path)
        old_info = previous_files.get(rel_path)
        
        if old_info is None:
            # New file
            change = FileChange(
                path=rel_path,
                change_type=ChangeType.ADDED,
                new_hash=new_hash,
                language=language
            )
            added.append(rel_path)
        elif old_info.get("hash") != new_hash:
            # Modified file
            change = FileChange(
                path=rel_path,
                change_type=ChangeType.MODIFIED,
                old_hash=old_info.get("hash"),
                new_hash=new_hash,
                language=language
            )
            modified.append(rel_path)
        else:
            # Unchanged file
            change = FileChange(
                path=rel_path,
                change_type=ChangeType.UNCHANGED,
                old_hash=old_info.get("hash"),
                new_hash=new_hash,
                language=language
            )
            unchanged.append(rel_path)
        
        current_files[rel_path] = change
    
    # Detect deleted files
    for old_path in previous_files:
        if old_path not in current_paths:
            old_info = previous_files[old_path]
            change = FileChange(
                path=old_path,
                change_type=ChangeType.DELETED,
                old_hash=old_info.get("hash"),
                language=old_info.get("language")
            )
            current_files[old_path] = change
            deleted.append(old_path)
    
    return ScanResult(
        files=current_files,
        added=added,
        modified=modified,
        deleted=deleted,
        unchanged=unchanged
    )


def apply_scan_to_state(state: Dict[str, Any], scan_result: ScanResult, repo: Repository) -> None:
    """
    Apply scan results to the state dictionary.
    
    Args:
        state: State dictionary to update (modified in place)
        scan_result: Results from scan_repository()
        repo: Repository context
    """
    # Update repo metadata
    state["repo"] = repo.to_dict()
    state["last_scan"] = datetime.now(timezone.utc).isoformat()
    
    # Update files - remove deleted, update/add others
    new_files = {}
    for path, change in scan_result.files.items():
        if change.change_type != ChangeType.DELETED:
            new_files[path] = change.to_dict()
    
    state["files"] = new_files

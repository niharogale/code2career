# autodoc/core/scan.py

from pathlib import Path
from typing import Dict, Any
import hashlib
import os

from autodoc.core.state import update_file, remove_file


def compute_file_hash(path: Path) -> str:
    """
    Compute a stable hash for a file's contents.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_repository(repo_root: Path, state: Dict[str, Any]) -> None:
    """
    Walk the repository and update state['files'] to reflect current contents.
    """
    # You will fill this in.
    # High-level steps:
    # 1. Build a set of all current files
    # 2. Compare against state['files']
    # 3. Call update_file / remove_file accordingly
    pass

# autodoc/core/repository.py

"""
Repository context class providing unified access to repository information.
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

# File extensions we consider as source code
SOURCE_EXTENSIONS: Set[str] = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
}

# Directories to always ignore during scanning
IGNORE_DIRS: Set[str] = {
    ".git",
    ".autodoc",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
}


@dataclass
class Repository:
    """
    Unified context for a repository, providing access to:
    - Repository root path
    - Git information (branch, commit)
    - File discovery
    """

    root: Path
    name: str
    branch: Optional[str] = None
    commit: Optional[str] = None
    autodoc_dir: Path = field(init=False)

    def __post_init__(self):
        self.autodoc_dir = self.root / ".autodoc"

    @classmethod
    def from_cwd(cls) -> "Repository":
        """
        Create a Repository context from the current working directory.
        Attempts to find git root if in a git repository.
        """
        cwd = Path.cwd()
        root = cls._find_git_root(cwd) or cwd
        name = root.name

        branch = cls._get_git_branch(root)
        commit = cls._get_git_commit(root)

        return cls(root=root, name=name, branch=branch, commit=commit)

    @classmethod
    def from_path(cls, path: Path) -> "Repository":
        """
        Create a Repository context from a specified path.
        """
        root = path.resolve()
        if not root.exists():
            raise ValueError(f"Path does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"Path is not a directory: {root}")

        name = root.name
        branch = cls._get_git_branch(root)
        commit = cls._get_git_commit(root)

        return cls(root=root, name=name, branch=branch, commit=commit)

    @staticmethod
    def _find_git_root(start: Path) -> Optional[Path]:
        """
        Walk up the directory tree to find the git root.
        Returns None if not in a git repository.
        """
        current = start.resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        # Check root directory
        if (current / ".git").exists():
            return current
        return None

    @staticmethod
    def _get_git_branch(root: Path) -> Optional[str]:
        """
        Get the current git branch name.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    @staticmethod
    def _get_git_commit(root: Path) -> Optional[str]:
        """
        Get the current git commit hash (short form).
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def is_initialized(self) -> bool:
        """
        Check if autodoc is initialized in this repository.
        """
        return self.autodoc_dir.exists()

    def get_state_path(self) -> Path:
        """
        Get the path to the state file.
        """
        return self.autodoc_dir / "state.json"

    def get_config_path(self) -> Path:
        """
        Get the path to the config file.
        """
        return self.autodoc_dir / "config.yaml"

    def get_files(
        self,
        extensions: Optional[Set[str]] = None,
        ignore_dirs: Optional[Set[str]] = None,
    ) -> List[Path]:
        """
        Discover all source files in the repository.

        Args:
            extensions: Set of file extensions to include (default: SOURCE_EXTENSIONS)
            ignore_dirs: Set of directory names to ignore (default: IGNORE_DIRS)

        Returns:
            Sorted list of file paths relative to repository root.
        """
        if extensions is None:
            extensions = SOURCE_EXTENSIONS
        if ignore_dirs is None:
            ignore_dirs = IGNORE_DIRS

        source_files: List[Path] = []

        for dirpath, dirnames, filenames in os.walk(self.root):
            # Filter out ignored directories (modifying in-place to prevent descent)
            dirnames[:] = [
                d for d in dirnames
                if d not in ignore_dirs and not any(
                    d.endswith(pattern.lstrip("*")) for pattern in ignore_dirs if "*" in pattern
                )
            ]

            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in extensions:
                    full_path = Path(dirpath) / filename
                    # Store as relative path from repo root
                    rel_path = full_path.relative_to(self.root)
                    source_files.append(rel_path)

        source_files.sort()
        return source_files

    def get_absolute_path(self, relative_path: Path) -> Path:
        """
        Convert a relative path to an absolute path within the repository.
        """
        return self.root / relative_path

    def to_dict(self) -> dict:
        """
        Serialize repository info for state storage.
        """
        return {
            "name": self.name,
            "root": str(self.root),
            "branch": self.branch or "",
            "commit": self.commit or "",
        }

    def __repr__(self) -> str:
        return f"Repository(name={self.name!r}, root={self.root}, branch={self.branch!r})"

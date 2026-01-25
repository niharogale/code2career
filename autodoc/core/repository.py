# autodoc/core/repository.py
"""
Repository context module - provides unified access to repository information.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from autodoc.core.exceptions import RepositoryNotFoundError

# File extensions we consider as source code
SOURCE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
}

# Directories to ignore during scanning
IGNORE_DIRS = {
    ".git",
    ".autodoc",
    ".venv",
    "venv",
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

# Files to always include (documentation files)
DOC_FILES = {
    "README.md",
    "README.rst",
    "README.txt",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
}


@dataclass
class Repository:
    """
    Unified repository context providing access to repo metadata and files.
    """
    root: Path
    name: str
    branch: str
    commit: str

    @classmethod
    def from_path(cls, path: Optional[Path] = None) -> "Repository":
        """
        Create a Repository context from a path (defaults to current directory).
        
        Args:
            path: Path to the repository root. If None, uses current working directory.
            
        Returns:
            Repository instance with git metadata populated.
            
        Raises:
            ValueError: If the path is not a valid git repository.
        """
        root = Path(path) if path else Path.cwd()
        root = root.resolve()
        
        # Verify it's a git repository
        git_dir = root / ".git"
        if not git_dir.exists():
            raise RepositoryNotFoundError(str(root))
        
        # Get git metadata
        name = root.name
        branch = cls._get_git_branch(root)
        commit = cls._get_git_commit(root)
        
        return cls(root=root, name=name, branch=branch, commit=commit)
    
    @classmethod
    def from_cwd(cls) -> "Repository":
        """
        Create a Repository context from the current working directory.
        Convenience method for the common case.
        """
        return cls.from_path(Path.cwd())
    
    @staticmethod
    def _get_git_branch(root: Path) -> str:
        """Get the current git branch name."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    @staticmethod
    def _get_git_commit(root: Path) -> str:
        """Get the current git commit hash (short form)."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def get_autodoc_dir(self) -> Path:
        """Return the .autodoc directory path."""
        return self.root / ".autodoc"
    
    def is_initialized(self) -> bool:
        """Check if autodoc has been initialized in this repository."""
        return self.get_autodoc_dir().exists()
    
    def get_files(self) -> List[str]:
        """
        Get all source files in the repository as relative path strings.
        
        Returns:
            List of relative path strings for all source files, sorted alphabetically.
        """
        source_files = []
        
        for path in self._walk_files():
            ext = path.suffix.lower()
            if ext in SOURCE_EXTENSIONS or path.name in DOC_FILES:
                rel_path = self.get_relative_path(path)
                source_files.append(rel_path)
        
        source_files.sort()
        return source_files
    
    def get_source_files(self) -> List[Path]:
        """
        Get all source files in the repository.
        
        Returns:
            List of Path objects for all source files, sorted alphabetically.
        """
        source_files = []
        
        for path in self._walk_files():
            ext = path.suffix.lower()
            if ext in SOURCE_EXTENSIONS or path.name in DOC_FILES:
                source_files.append(path)
        
        source_files.sort()
        return source_files
    
    def get_all_files(self) -> List[Path]:
        """
        Get all files in the repository (excluding ignored directories).
        
        Returns:
            List of Path objects for all files, sorted alphabetically.
        """
        files = list(self._walk_files())
        files.sort()
        return files
    
    def _walk_files(self):
        """
        Generator that yields all files, respecting ignore patterns.
        """
        for item in self.root.rglob("*"):
            if item.is_file() and not self._should_ignore(item):
                yield item
    
    def _should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored based on ignore patterns.
        """
        parts = path.relative_to(self.root).parts
        
        for part in parts:
            # Check exact directory matches
            if part in IGNORE_DIRS:
                return True
            # Check .egg-info pattern
            if part.endswith(".egg-info"):
                return True
        
        return False
    
    def get_language(self, path: Path) -> Optional[str]:
        """
        Get the programming language for a file based on its extension.
        
        Args:
            path: Path to the file
            
        Returns:
            Language name string, or None if not a recognized source file.
        """
        ext = path.suffix.lower()
        return SOURCE_EXTENSIONS.get(ext)
    
    def get_relative_path(self, path: Path) -> str:
        """
        Get the path relative to the repository root.
        
        Args:
            path: Absolute or relative path
            
        Returns:
            String path relative to repo root.
        """
        if path.is_absolute():
            return str(path.relative_to(self.root))
        return str(path)
    
    def get_absolute_path(self, rel_path: str) -> Path:
        """
        Get the absolute path from a relative path string.
        
        Args:
            rel_path: Path relative to repo root (as string)
            
        Returns:
            Absolute Path object.
        """
        return self.root / rel_path
    
    def to_dict(self) -> dict:
        """
        Convert repository metadata to a dictionary for state storage.
        """
        return {
            "name": self.name,
            "root": str(self.root),
            "branch": self.branch,
            "commit": self.commit
        }

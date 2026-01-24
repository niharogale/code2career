# autodoc/core/protocols.py
"""
Protocol definitions for autodoc.

This module defines typing protocols that establish clean contracts for core
autodoc components. These protocols enable future extensibility (e.g., swapping
implementations, adding new generator types) without breaking existing code.

Protocols follow PEP 544 structural subtyping - classes don't need to explicitly
inherit from these protocols; they just need to implement the required methods.
"""

from pathlib import Path
from typing import Dict, Any, List, Protocol, runtime_checkable


@runtime_checkable
class StateManager(Protocol):
    """
    Protocol for state management operations.
    
    Implementations handle loading and saving autodoc state (e.g., tracked files,
    last scan time, repository metadata). This abstraction allows swapping between
    JSON files, databases, or other storage backends.
    """
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load the current state.
        
        Returns:
            Dictionary containing the state data with keys like 'version', 'repo',
            'files', 'last_scan', etc.
        """
        ...
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Save the state.
        
        Args:
            state: Dictionary containing the state data to persist.
        """
        ...
    
    def get_state_path(self) -> Path:
        """
        Get the path where state is stored.
        
        Returns:
            Path to the state storage location.
        """
        ...


@runtime_checkable
class Scanner(Protocol):
    """
    Protocol for repository scanning operations.
    
    Implementations enumerate files in a repository, compute hashes, and detect
    changes since the last scan. This abstraction allows different scanning
    strategies (e.g., git-aware scanning, filesystem-only scanning).
    """
    
    def scan_repository(self, repo: Any, previous_state: Dict[str, Any]) -> Any:
        """
        Scan a repository and detect changes.
        
        Args:
            repo: Repository context (typically a Repository instance).
            previous_state: State dictionary from the previous scan.
            
        Returns:
            ScanResult or similar object containing detected changes.
        """
        ...
    
    def compute_file_hash(self, path: Path) -> str:
        """
        Compute a hash for a file's contents.
        
        Args:
            path: Path to the file to hash.
            
        Returns:
            Hash string (typically hex digest).
        """
        ...


@runtime_checkable
class Generator(Protocol):
    """
    Protocol for documentation generation operations.
    
    Implementations generate documentation files (e.g., README.md) based on
    repository state and analysis. This abstraction allows multiple generator
    types (README, API docs, changelog, etc.) with a consistent interface.
    """
    
    def generate(self, state: Dict[str, Any], output_path: Path, dry_run: bool = False) -> str:
        """
        Generate documentation.
        
        Args:
            state: Current state dictionary with repository and file information.
            output_path: Path where the generated documentation should be written.
            dry_run: If True, return the content without writing to disk.
            
        Returns:
            The generated documentation content as a string.
        """
        ...
    
    def analyze_project(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the project to gather information for generation.
        
        Args:
            state: Current state dictionary with repository and file information.
            
        Returns:
            Dictionary containing analysis results (e.g., detected language,
            frameworks, project structure).
        """
        ...


@runtime_checkable
class ConfigLoader(Protocol):
    """
    Protocol for configuration loading operations.
    
    Implementations load and save autodoc configuration from various sources
    (e.g., YAML files, TOML files, environment variables). This abstraction
    allows flexible configuration management.
    """
    
    def load_config(self, config_path: Path) -> Any:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            Configuration object (typically an AutodocConfig instance).
        """
        ...
    
    def save_config(self, config: Any, config_path: Path) -> None:
        """
        Save configuration to a file.
        
        Args:
            config: Configuration object to save.
            config_path: Path where the configuration should be written.
        """
        ...
    
    def get_default_config(self) -> Any:
        """
        Get default configuration.
        
        Returns:
            Configuration object with default values.
        """
        ...


@runtime_checkable
class Repository(Protocol):
    """
    Protocol for repository operations.
    
    Implementations provide access to repository metadata and file operations.
    This abstraction allows working with different version control systems
    or non-VCS directories.
    """
    
    def get_source_files(self) -> List[Path]:
        """
        Get all source files in the repository.
        
        Returns:
            List of Path objects for tracked source files.
        """
        ...
    
    def get_relative_path(self, file_path: Path) -> str:
        """
        Get the relative path of a file from the repository root.
        
        Args:
            file_path: Absolute or relative path to a file.
            
        Returns:
            Relative path string from repository root.
        """
        ...
    
    def get_language(self, file_path: Path) -> str:
        """
        Detect the programming language of a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Language identifier (e.g., 'python', 'javascript').
        """
        ...
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert repository metadata to a dictionary.
        
        Returns:
            Dictionary with repository information (name, root, branch, commit).
        """
        ...

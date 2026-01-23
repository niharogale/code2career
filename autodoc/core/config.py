# autodoc/core/config.py
"""
Configuration management module for autodoc.

This module provides the AutodocConfig dataclass for managing application configuration,
including loading from and saving to YAML files.
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from autodoc.core.exceptions import ConfigError


@dataclass
class AutodocConfig:
    """
    Configuration settings for autodoc.
    
    This dataclass holds all configuration options that can be customized
    through the config.yaml file or overridden via CLI flags.
    """
    
    # File pattern settings
    include_patterns: List[str] = field(default_factory=lambda: [
        "*.py",
        "*.js",
        "*.ts",
        "*.tsx",
        "*.jsx",
        "*.java",
        "*.go",
        "*.rs",
        "*.rb",
        "*.php",
        "*.c",
        "*.cpp",
        "*.h",
        "*.hpp",
        "*.cs",
        "*.swift",
        "*.kt",
        "*.scala",
        "*.sh",
        "*.bash",
        "*.zsh",
        "README.*",
        "CHANGELOG.*",
        "CONTRIBUTING.*",
        "LICENSE*",
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
    ])
    
    exclude_patterns: List[str] = field(default_factory=lambda: [
        ".git/**",
        ".autodoc/**",
        ".venv/**",
        "venv/**",
        "env/**",
        ".env/**",
        "node_modules/**",
        "__pycache__/**",
        ".pytest_cache/**",
        ".mypy_cache/**",
        ".tox/**",
        "dist/**",
        "build/**",
        ".eggs/**",
        "*.egg-info/**",
    ])
    
    # README section configuration
    readme_sections: List[str] = field(default_factory=lambda: [
        "title",
        "description",
        "features",
        "installation",
        "usage",
        "structure",
        "contributing",
        "license",
    ])
    
    # CLI default settings
    verbose: bool = False
    dry_run: bool = False
    
    @classmethod
    def default(cls) -> "AutodocConfig":
        """
        Create a default configuration instance.
        
        Returns:
            AutodocConfig with default values.
        """
        return cls()
    
    @classmethod
    def from_file(cls, config_path: Path) -> "AutodocConfig":
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the config.yaml file.
            
        Returns:
            AutodocConfig instance populated from the YAML file.
            
        Raises:
            ConfigError: If the file is malformed or contains invalid values.
        """
        if not config_path.exists():
            # Return default config if file doesn't exist
            return cls.default()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            # Handle empty file or null content
            if data is None:
                return cls.default()
            
            # Validate that data is a dictionary
            if not isinstance(data, dict):
                raise ConfigError(f"Config file must contain a YAML mapping, got {type(data).__name__}")
            
            # Extract configuration values with defaults
            config = cls(
                include_patterns=data.get("include_patterns", cls.default().include_patterns),
                exclude_patterns=data.get("exclude_patterns", cls.default().exclude_patterns),
                readme_sections=data.get("readme_sections", cls.default().readme_sections),
                verbose=data.get("verbose", cls.default().verbose),
                dry_run=data.get("dry_run", cls.default().dry_run),
            )
            
            return config
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse YAML: {e}")
        except IOError as e:
            raise ConfigError(f"Failed to read config file: {e}")
    
    @classmethod
    def from_autodoc_dir(cls, autodoc_dir: Path) -> "AutodocConfig":
        """
        Load configuration from the .autodoc directory.
        
        Convenience method that constructs the config.yaml path from
        the .autodoc directory path.
        
        Args:
            autodoc_dir: Path to the .autodoc directory.
            
        Returns:
            AutodocConfig instance loaded from .autodoc/config.yaml.
            
        Raises:
            ConfigError: If the config file is malformed.
        """
        config_path = autodoc_dir / "config.yaml"
        return cls.from_file(config_path)
    
    def save(self, config_path: Path) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            config_path: Path where the config.yaml file should be written.
            
        Raises:
            ConfigError: If the file cannot be written.
        """
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary and add comments as a separate structure
            config_dict = self.to_dict()
            
            # Create YAML with comments
            yaml_content = self._generate_yaml_with_comments(config_dict)
            
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)
                
        except IOError as e:
            raise ConfigError(f"Failed to write config file: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the configuration.
        """
        return asdict(self)
    
    def _generate_yaml_with_comments(self, config_dict: Dict[str, Any]) -> str:
        """
        Generate YAML content with helpful comments.
        
        Args:
            config_dict: Configuration dictionary to serialize.
            
        Returns:
            YAML string with comments.
        """
        def quote_if_needed(s: str) -> str:
            """Quote strings that contain special YAML characters."""
            # Quote if it contains *, ?, [, ], {, }, :, -, |, >, <, !, &, %, @, `
            special_chars = ['*', '?', '[', ']', '{', '}', ':', '-', '|', '>', '<', '!', '&', '%', '@', '`']
            if any(char in s for char in special_chars):
                # Use single quotes and escape any single quotes in the string
                return f"'{s.replace(chr(39), chr(39) + chr(39))}'"
            return s
        
        lines = [
            "# AutoDoc Configuration File",
            "# This file controls how autodoc scans and generates documentation for your repository.",
            "",
            "# File patterns to include when scanning (glob patterns)",
            "# These patterns determine which files are considered source code or documentation",
        ]
        
        lines.append("include_patterns:")
        for pattern in config_dict["include_patterns"]:
            lines.append(f"  - {quote_if_needed(pattern)}")
        
        lines.extend([
            "",
            "# File patterns to exclude when scanning (glob patterns)",
            "# These patterns determine which files and directories are ignored",
        ])
        
        lines.append("exclude_patterns:")
        for pattern in config_dict["exclude_patterns"]:
            lines.append(f"  - {quote_if_needed(pattern)}")
        
        lines.extend([
            "",
            "# README sections to generate (in order)",
            "# Available sections: title, description, features, installation, usage, structure, contributing, license",
        ])
        
        lines.append("readme_sections:")
        for section in config_dict["readme_sections"]:
            lines.append(f"  - {quote_if_needed(section)}")
        
        lines.extend([
            "",
            "# Default CLI flags",
            "# These can be overridden by command-line arguments",
            f"verbose: {str(config_dict['verbose']).lower()}",
            f"dry_run: {str(config_dict['dry_run']).lower()}",
            "",
        ])
        
        return "\n".join(lines)

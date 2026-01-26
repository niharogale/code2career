# AutoDoc Architecture

## Overview

AutoDoc is a tool for automatic README and documentation generation for GitHub repositories. It follows a phased development approach, with Phase 1 (Foundation) and Phase 2 (Clean Interfaces) now complete.

## Development Status

- ✅ **Phase 1: Foundation (Complete)** - Working end-to-end flow with file scanning and basic README generation
- ✅ **Phase 2: Clean Interfaces (Complete)** - Configuration management, custom exceptions, protocols, and enhanced CLI
- 🚧 **Phase 3: Intelligent Analysis** - AST parsing, dependency graphs, semantic change detection
- 🚧 **Phase 4: Polish** - Watch mode, GitHub Actions, PyPI publication

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         CLI Layer (commands/)           │
│  init, scan, generate (with flags)      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Core Layer (core/)              │
│  • Config: YAML configuration           │
│  • State: JSON state persistence        │
│  • Repository: Git repo context         │
│  • Exceptions: Custom error hierarchy   │
│  • Protocols: Interface definitions     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Analysis Layer (analysis/)           │
│  File scanning and change detection     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   Generation Layer (generation/)        │
│  README generation with heuristics      │
└─────────────────────────────────────────┘
```

## Core Modules

### CLI Commands (`autodoc/commands/`)
- **init.py**: Initialize `.autodoc/` directory with config and state
  - Flags: `--force` to reinitialize
- **scan.py**: Scan repository and detect file changes
  - Flags: `--verbose`, `--dry-run`
- **generate.py**: Generate README and resume bullets
  - Flags: `--verbose`, `--dry-run`, `--output`

### Core Domain (`autodoc/core/`)
- **config.py**: Configuration management with YAML support
  - `AutodocConfig` dataclass with file patterns, sections, CLI defaults
  - Load from `.autodoc/config.yaml` with fallback to defaults
- **state.py**: State persistence in `.autodoc/state.json`
  - Tracks file hashes, last scan time, repository metadata
  - Validation with logging for corrupted state
- **repository.py**: Unified repository context
  - Git metadata extraction (branch, commit, name)
  - Source file enumeration with language detection
- **exceptions.py**: Custom exception hierarchy
  - `AutodocError` (base), `NotInitializedError`, `RepositoryNotFoundError`, `StateCorruptedError`, `ConfigError`
- **protocols.py**: Typing protocols for extensibility
  - `StateManager`, `Scanner`, `Generator`, `ConfigLoader`, `Repository`
- **scan.py**: File scanning and change detection
  - SHA-256 hashing, diff with previous state
  - Returns `ScanResult` with added/modified/deleted/unchanged files

### Generation Layer (`autodoc/generation/`)
- **readme_generator.py**: README generation with heuristics
  - Project type analysis (language, package manager, frameworks)
  - Section generators: overview, installation, usage, structure

## Configuration System

Configuration is stored in `.autodoc/config.yaml`:

```yaml
# File patterns to include/exclude
include_patterns:
  - '*.py'
  - '*.js'
  - 'README.*'
  
exclude_patterns:
  - '.git/**'
  - 'node_modules/**'
  - '__pycache__/**'

# README sections to generate
readme_sections:
  - title
  - description
  - installation
  - usage
  - structure
  - license

# Default CLI flags
verbose: false
dry_run: false
```

## Exception Hierarchy

```
Exception
  └── AutodocError
      ├── NotInitializedError    (run 'autodoc init')
      ├── RepositoryNotFoundError (not a git repo)
      ├── StateCorruptedError    (invalid state.json)
      └── ConfigError            (malformed config.yaml)
```

All autodoc exceptions inherit from `AutodocError`, allowing users to catch all autodoc-specific errors with a single except clause.

## State Model

Location: `.autodoc/state.json`

```json
{
  "version": "1.0",
  "repo": {
    "name": "autodoc",
    "root": "/path/to/repo",
    "branch": "main",
    "commit": "abc123"
  },
  "last_scan": "2026-01-25T12:00:00Z",
  "files": {
    "src/main.py": {
      "hash": "sha256:...",
      "language": "python",
      "last_modified": "2026-01-25T11:00:00Z",
      "change_type": "modified"
    }
  },
  "readme_sections": {}
}
```

## Scan Control Flow

```
autodoc scan [--verbose] [--dry-run]
  -> load config from .autodoc/config.yaml
  -> load state from .autodoc/state.json
  -> Repository.from_cwd()
  -> scan_repository(repo, state)
      -> discover source files
      -> compute SHA-256 hashes
      -> diff with previous state
      -> classify as added/modified/deleted/unchanged
  -> apply_scan_to_state(state, scan_result)
  -> save_state() (unless --dry-run)
  -> display summary
```

## Generate Control Flow

```
autodoc generate readme [--verbose] [--dry-run] [--output PATH]
  -> load config and state
  -> analyze_project_type(state)
      -> detect language, package manager, frameworks
  -> generate_readme(state)
      -> generate_overview_section()
      -> generate_installation_section()
      -> generate_usage_section()
      -> generate_structure_section()
  -> write_readme() (unless --dry-run)
```

## Protocol Interfaces

Protocols define clean contracts for future extensibility:

- **StateManager**: Load/save state operations (future: swap JSON for database)
- **Scanner**: Repository scanning interface (future: git-aware scanning)
- **Generator**: Documentation generation (future: multiple doc types)
- **ConfigLoader**: Configuration loading (future: TOML, env vars)
- **Repository**: Repository operations (future: non-git repos)

## Testing

Test coverage: 62 tests across 5 test modules

- `test_change_detection.py`: File scanning and change detection (12 tests)
- `test_repository.py`: Repository context and metadata (12 tests)
- `test_state.py`: State persistence and validation (10 tests)
- `test_config.py`: Configuration loading and saving (14 tests)
- `test_exceptions.py`: Exception hierarchy and messages (14 tests)

Fixtures in `conftest.py`:
- `temp_git_repo`: Temporary git repository
- `sample_repo`: Repository instance
- `empty_state`: Default state dictionary
- `sample_python_project`: Python project structure
- `autodoc_initialized_repo`: Repo with `.autodoc/` initialized
- `sample_config`: Sample configuration instance

## Future Work (Phase 3+)

- **AST Parsing**: Use tree-sitter for semantic code analysis
- **Dependency Graphs**: Build import/dependency graphs
- **Semantic Change Detection**: Classify changes as breaking/additive/docs-only
- **LLM Integration**: Generate intelligent summaries and descriptions
- **Incremental Updates**: Update only affected README sections
- **Watch Mode**: Continuous documentation updates
- **GitHub Actions**: CI/CD integration
- **Resume Generation**: Portfolio bullet point generation

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation for PyPI
- Complete package metadata and build configuration
- MIT License
- Contributing guidelines
- PyPI publish workflow

## [0.1.0] - 2026-02-02

### Added
- Core autodoc functionality
- CLI commands: `init`, `scan`, `generate`, `watch`
- Multi-language AST parsing (Python, JavaScript, TypeScript)
- Dependency graph analysis
- Semantic change detection
- README generation with intelligent project analysis
- Resume bullet generation from commit history
- File watching for continuous documentation updates
- State persistence and change tracking
- GitHub Actions workflows for CI/CD
- Comprehensive test suite
- Architecture documentation

### Features

#### CLI Commands
- **init**: Initialize `.autodoc/` directory with config and state
- **scan**: Scan repository and detect file changes with AST analysis
- **generate readme**: Generate README with project structure and API docs
- **generate resume**: Generate resume bullets from commit history
- **watch**: Continuous documentation updates with file watching

#### Code Analysis
- AST parsing using tree-sitter
- Import dependency tracking
- Semantic change classification (breaking, additive, internal, docs-only)
- Public/private API detection
- Multi-language support (Python, JavaScript, TypeScript)

#### Documentation Generation
- Intelligent project type detection
- Automatic installation instructions
- API reference from AST definitions
- Project structure visualization
- Framework and tool detection

#### State Management
- SHA-256 file hashing for change detection
- AST hash computation for semantic analysis
- Import and definition tracking
- Dependency graph persistence
- Configuration management with YAML

[Unreleased]: https://github.com/niharo/autodoc/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/niharo/autodoc/releases/tag/v0.1.0

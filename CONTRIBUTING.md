# Contributing to AutoDoc

Thank you for your interest in contributing to AutoDoc! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/autodoc.git
   cd autodoc
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/niharo/autodoc.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- pip

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Verify the installation:
   ```bash
   autodoc --help
   ```

## Project Structure

```
autodoc/
├── autodoc/
│   ├── cli.py              # CLI entry point
│   ├── commands/           # CLI commands (init, scan, generate, watch)
│   ├── core/               # Core domain logic (config, state, repository)
│   ├── analysis/           # Code analysis (AST, dependencies, semantic changes)
│   └── generation/         # Documentation generation (README, resume)
├── tests/                  # Test suite (unit and integration tests)
├── .github/
│   └── workflows/          # CI/CD workflows
├── pyproject.toml          # Package configuration
├── ARCHITECTURE.md         # Architecture documentation
└── README.md               # User documentation
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### Making Changes

1. **Write code** following our [code style guidelines](#code-style)
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Run tests** to ensure everything works
5. **Commit changes** with clear messages

### Commit Message Guidelines

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no logic changes)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat(cli): add watch command for continuous documentation updates

fix(ast): handle empty files without crashing

docs(readme): add installation instructions for Windows users

test(state): add tests for state migration
```

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_config.py
```

Run specific test:
```bash
pytest tests/test_config.py::test_load_default_config
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures from `conftest.py` for common setup
- Aim for high test coverage (especially for core functionality)

**Example test:**
```python
def test_scan_detects_changes(sample_repo, empty_state):
    """Test that scanning detects file changes correctly."""
    # Create a test file
    test_file = sample_repo.root / "test.py"
    test_file.write_text("print('hello')")
    
    # Scan the repository
    result = scan_repository(sample_repo, empty_state)
    
    # Verify the file was detected
    assert "test.py" in result.added
```

### Integration Tests

Integration tests run as part of the CI workflow and test the full CLI:

```bash
# Initialize autodoc
autodoc init

# Scan repository
autodoc scan --verbose

# Generate documentation
autodoc generate readme --dry-run
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Use absolute imports, group by stdlib/third-party/local
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Formatting and Linting

We use the following tools:

- **Black** - Code formatter
- **Ruff** - Fast Python linter
- **MyPy** - Static type checker

Run formatters and linters:

```bash
# Format code with black
black autodoc/

# Check formatting
black --check autodoc/

# Lint with ruff
ruff check autodoc/

# Type check with mypy
mypy autodoc/ --ignore-missing-imports
```

### Pre-commit Checks

Before committing, ensure:

1. ✅ All tests pass: `pytest`
2. ✅ Code is formatted: `black --check autodoc/`
3. ✅ No linting errors: `ruff check autodoc/`
4. ✅ Type hints are valid: `mypy autodoc/`

## Submitting Changes

### Pull Request Process

1. **Update your fork** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a pull request** on GitHub:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

### Pull Request Guidelines

- **Title**: Clear and descriptive (e.g., "Add watch command for continuous updates")
- **Description**: Explain what changes you made and why
- **Link issues**: Reference related issues (e.g., "Fixes #123")
- **Tests**: Ensure all tests pass and add new tests for new features
- **Documentation**: Update docs if your changes affect user-facing behavior
- **Small PRs**: Keep PRs focused and reasonably sized

### PR Review Process

1. Automated checks run (tests, linting, type checking)
2. Maintainers review your code
3. Address feedback by pushing additional commits
4. Once approved, maintainers will merge your PR

## Reporting Issues

### Bug Reports

When reporting a bug, include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Minimal steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, autodoc version
- **Logs/Screenshots**: Error messages, stack traces, or screenshots

**Example:**

```markdown
**Description:**
`autodoc scan` crashes when encountering a file with invalid UTF-8 encoding.

**Steps to reproduce:**
1. Create a file with invalid UTF-8 bytes
2. Run `autodoc scan`

**Expected behavior:**
Should skip the file with a warning

**Actual behavior:**
Crashes with UnicodeDecodeError

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.11.2
- autodoc: 0.1.0

**Error message:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 10
```
```

### Feature Requests

When requesting a feature, include:

- **Description**: Clear description of the feature
- **Use case**: Why you need this feature
- **Proposed solution**: How you envision it working
- **Alternatives**: Other approaches you've considered

## Development Tips

### Testing Your Changes Locally

Test your changes on a real repository:

```bash
# In your test repository
autodoc init
autodoc scan --verbose
autodoc generate readme --dry-run --verbose
```

### Debugging

Use the `--verbose` flag for detailed output:

```bash
autodoc scan --verbose
autodoc generate readme --verbose
```

### Working with State

The state file (`.autodoc/state.json`) tracks repository metadata. To reset:

```bash
autodoc init --force
```

### AST Parsing

When working on AST parsing features:

1. Check `autodoc/analysis/ast_parser.py` for the parser implementation
2. Add language support by adding tree-sitter grammars
3. Test with real code files in various languages

## Questions?

If you have questions:

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
2. Search existing [issues](https://github.com/niharo/autodoc/issues)
3. Open a new issue with the "question" label

## License

By contributing to AutoDoc, you agree that your contributions will be licensed under the MIT License.

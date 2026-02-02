# AutoDoc

**Automatic README and resume generation for GitHub repositories.**

AutoDoc is an intelligent documentation generator that analyzes your codebase using Abstract Syntax Tree (AST) parsing, builds dependency graphs, detects semantic changes, and automatically generates comprehensive documentation. Perfect for keeping your README up-to-date and creating professional resume bullets from your git history.

[![CI](https://github.com/niharo/autodoc/workflows/CI/badge.svg)](https://github.com/niharo/autodoc/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **🎯 Intelligent Code Analysis** - Multi-language AST parsing (Python, JavaScript, TypeScript) using tree-sitter
- **📊 Dependency Tracking** - Automatic dependency graph construction with circular dependency detection
- **🔍 Semantic Change Detection** - Classifies changes as breaking, additive, or internal
- **📝 Smart README Generation** - Analyzes project structure, frameworks, and generates comprehensive documentation
- **💼 Resume Bullet Generation** - Creates professional resume bullets from git commit history
- **👀 Watch Mode** - Continuous documentation updates with file watching
- **⚡ Fast & Efficient** - Incremental scans with AST caching for optimal performance
- **🔧 Highly Configurable** - YAML-based configuration with sensible defaults

---

## 📦 Installation

### From PyPI

```bash
pip install autodoc
```

### From Source

```bash
git clone https://github.com/niharo/autodoc.git
cd autodoc
pip install -e .
```

### Requirements

- Python 3.9 or higher
- Git repository

---

## 🚀 Quick Start

```bash
# Navigate to your git repository
cd /path/to/your/project

# Initialize AutoDoc
autodoc init

# Scan your codebase
autodoc scan

# Generate README
autodoc generate readme
```

That's it! AutoDoc will analyze your code and create a comprehensive README.md.

---

## 📚 Usage

### Initialize AutoDoc

Create `.autodoc/` directory with configuration and state tracking:

```bash
autodoc init
```

Options:
- `--force, -f` - Reinitialize even if already exists

---

### Scan Repository

Analyze your codebase and detect changes:

```bash
autodoc scan --verbose
```

Options:
- `--verbose, -v` - Show detailed scanning output
- `--dry-run, -n` - Preview changes without saving state

**What it does:**
- Computes SHA-256 hashes for change detection
- Parses AST for supported languages
- Extracts imports, definitions, and dependencies
- Builds dependency graph
- Tracks semantic changes

---

### Generate README

Create or update your README based on scan results:

```bash
autodoc generate readme
```

Options:
- `--output, -o PATH` - Output path (default: `README.md`)
- `--dry-run, -n` - Preview without writing
- `--verbose, -v` - Show detailed output

**Generated sections:**
- Project overview with language and framework detection
- Installation instructions (language-specific)
- Usage examples with entry point detection
- Project structure with core module identification
- API reference from AST definitions
- Recent changes with breaking change detection

---

### Generate Resume Bullets

Create professional resume bullets from your git history:

```bash
autodoc generate resume --max 10 --style detailed
```

Options:
- `--author, -a NAME` - Filter by author
- `--limit, -l N` - Max commits to analyze (default: 50)
- `--max, -m N` - Max bullets to generate (default: 5)
- `--style, -s STYLE` - Output style: `standard`, `detailed`, or `concise`
- `--output, -o PATH` - Export to JSON
- `--verbose, -v` - Show detailed output

**Example output:**

```
• Developed multi-language AST parser supporting Python, JavaScript, and TypeScript using tree-sitter, 
  enabling semantic code analysis across diverse codebases

• Implemented dependency graph analysis system tracking import relationships, detecting circular 
  dependencies, and performing topological sorting for build optimization

• Created semantic change detection engine classifying code modifications as breaking, additive, or 
  internal changes to improve documentation accuracy
```

---

### Watch Mode

Continuously monitor your repository and auto-update documentation:

```bash
autodoc watch --verbose
```

Options:
- `--interval, -i SECONDS` - Polling interval (default: 2)
- `--readme / --no-readme` - Auto-generate README (default: enabled)
- `--verbose, -v` - Show detailed output

Perfect for development workflows - documentation stays current as you code!

---

## 🏗️ Architecture

AutoDoc follows a layered architecture:

```
┌─────────────────────────────────────────┐
│         CLI Layer (commands/)           │
│  init, scan, generate, watch            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Core Layer (core/)              │
│  Config, State, Repository, Exceptions  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Analysis Layer (analysis/)           │
│  AST Parser, Dependency Graph, Changes  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   Generation Layer (generation/)        │
│  README & Resume Generation             │
└─────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

---

## 📖 Documentation

- **[API Documentation](docs/API.md)** - Complete API reference with examples
- **[Usage Examples](docs/EXAMPLES.md)** - Practical examples and common patterns
- **[Architecture](ARCHITECTURE.md)** - Technical architecture and design decisions
- **[Contributing](CONTRIBUTING.md)** - Development guidelines and how to contribute
- **[Changelog](CHANGELOG.md)** - Version history and release notes

---

## 🎯 Use Cases

### For Individual Developers

- **Keep README current** - Automatically update documentation as code evolves
- **Generate resume bullets** - Create professional bullets from your commits
- **Understand codebases** - Visualize dependencies and code structure
- **Track changes** - Identify breaking changes and API modifications

### For Teams

- **Enforce documentation standards** - Automated documentation in CI/CD
- **Onboard new developers** - Auto-generated architecture documentation
- **Review changes** - Semantic change detection for code reviews
- **Maintain consistency** - Uniform documentation across projects

### For Open Source

- **Attract contributors** - Professional, up-to-date README
- **Document APIs** - Auto-generated API reference from code
- **Show impact** - Generate changelogs from git history
- **Save time** - Focus on coding, not documentation maintenance

---

## 🛠️ Configuration

Customize AutoDoc behavior with `.autodoc/config.yaml`:

```yaml
# File patterns to include
include_patterns:
  - '*.py'
  - '*.js'
  - '*.ts'
  - '*.jsx'
  - '*.tsx'
  
# File patterns to exclude
exclude_patterns:
  - '.git/**'
  - 'node_modules/**'
  - '__pycache__/**'
  - 'venv/**'
  - 'dist/**'

# README sections to generate
readme_sections:
  - title
  - description
  - installation
  - usage
  - structure
  - api
  - license

# Default CLI flags
verbose: false
dry_run: false
```

---

## 🔧 Advanced Features

### Multi-Language Support

AutoDoc supports Python, JavaScript, and TypeScript with plans to add more languages:

```python
# Python example
from autodoc.core.repository import Repository

repo = Repository.from_cwd()
```

```javascript
// JavaScript example
import { analyzeProject } from 'autodoc-analyzer';

const analysis = analyzeProject('./src');
```

### Dependency Graph Analysis

Understand your codebase structure:

```bash
autodoc scan --verbose
```

AutoDoc automatically:
- Tracks import relationships
- Detects circular dependencies
- Identifies core modules (most imported)
- Finds entry points (not imported by others)
- Performs topological sorting for build order

### Semantic Change Detection

AutoDoc classifies changes into categories:

- **BREAKING** - Removed public APIs or signature changes
- **ADDITIVE** - New functions or optional parameters
- **INTERNAL** - Private method changes or refactoring
- **DOCS_ONLY** - Documentation-only changes (same AST)

---

## 🔄 CI/CD Integration

### GitHub Actions

Automatically update README on every push:

```yaml
name: Update Documentation

on:
  push:
    branches: [main]

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install autodoc
      - run: autodoc init --force
      - run: autodoc scan
      - run: autodoc generate readme
      - run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add README.md .autodoc/
          git commit -m "docs: update README [skip ci]" || exit 0
          git push
```

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for more integration examples.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

### Quick Contribution Setup

```bash
# Clone and setup
git clone https://github.com/niharo/autodoc.git
cd autodoc
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black autodoc/
ruff check autodoc/
```

---

## 📊 Project Statistics

- **Languages**: Python (primary), with multi-language AST support
- **Lines of Code**: ~5,000+ (excluding tests)
- **Test Coverage**: 60+ tests across 5 test modules
- **Dependencies**: 6 core dependencies (typer, pyyaml, tree-sitter, watchdog)
- **Python Versions**: 3.9, 3.10, 3.11, 3.12

---

## 🗺️ Roadmap

- [x] Multi-language AST parsing (Python, JavaScript, TypeScript)
- [x] Dependency graph analysis
- [x] Semantic change detection
- [x] README generation
- [x] Resume bullet generation
- [x] Watch mode for continuous updates
- [x] GitHub Actions integration
- [ ] LLM integration for intelligent summaries (OpenAI, Claude)
- [ ] More language support (Rust, Go, Java)
- [ ] Web UI for documentation preview
- [ ] VS Code extension
- [ ] Advanced metrics (complexity, test coverage correlation)
- [ ] Dependency graph visualization

---

## 📄 License

AutoDoc is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **tree-sitter** - Fast, incremental parsing library
- **typer** - Modern CLI framework
- **watchdog** - File system monitoring

---

## 📮 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/niharo/autodoc/issues)
- **Discussions**: [GitHub Discussions](https://github.com/niharo/autodoc/discussions)
- **Documentation**: [https://github.com/niharo/autodoc](https://github.com/niharo/autodoc)

---

## ⭐ Show Your Support

If AutoDoc helps you save time and improve your documentation, please consider:

- ⭐ **Starring the repository** on GitHub
- 🐛 **Reporting bugs** and suggesting features
- 📖 **Contributing** to documentation and code
- 📣 **Sharing** with your network

---

**Built with ❤️ by developers, for developers.**

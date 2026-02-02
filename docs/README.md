# AutoDoc Documentation

Welcome to the AutoDoc documentation! This guide will help you understand, use, and extend AutoDoc.

## 📚 Documentation Structure

### Getting Started

- **[Main README](../README.md)** - Overview, quick start, and basic usage
- **[Installation Guide](../README.md#-installation)** - How to install AutoDoc
- **[Quick Start](../README.md#-quick-start)** - Get started in 3 commands

### Usage Guides

- **[Usage Examples](EXAMPLES.md)** - Practical examples and common patterns
  - Basic workflows (init, scan, generate)
  - Advanced usage (watch mode, custom config)
  - CI/CD integration (GitHub Actions, pre-commit hooks)
  - Multi-language projects
  - Monorepo setups
  - Troubleshooting

### API Reference

- **[API Documentation](API.md)** - Complete API reference
  - CLI commands with all options
  - Core modules (config, state, repository)
  - Analysis modules (AST parser, dependency graph, semantic changes)
  - Generation modules (README, resume)
  - Exception hierarchy
  - Type definitions

### Architecture & Design

- **[Architecture](../ARCHITECTURE.md)** - Technical architecture and design decisions
  - System overview and layers
  - State model and versioning
  - AST parsing strategy
  - Dependency graph implementation
  - Performance characteristics
  - Design trade-offs

### Contributing

- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to AutoDoc
  - Development setup
  - Code style guidelines
  - Testing requirements
  - Pull request process
  - Commit message conventions

### Release Information

- **[Changelog](../CHANGELOG.md)** - Version history and release notes
- **[License](../LICENSE)** - MIT License

---

## 🎯 Quick Navigation

### I want to...

**Use AutoDoc**
- [Install AutoDoc](../README.md#-installation)
- [Run my first scan](EXAMPLES.md#1-first-time-setup)
- [Generate a README](EXAMPLES.md#1-first-time-setup)
- [Generate resume bullets](EXAMPLES.md#4-generating-resume-bullets)
- [Set up watch mode](EXAMPLES.md#3-continuous-documentation-updates)

**Configure AutoDoc**
- [Customize file patterns](EXAMPLES.md#5-custom-configuration)
- [Select README sections](EXAMPLES.md#5-custom-configuration)
- [Configure for monorepo](EXAMPLES.md#12-monorepo-setup)
- [Set up CI/CD](EXAMPLES.md#9-github-actions-workflow)

**Understand AutoDoc**
- [Architecture overview](../ARCHITECTURE.md#overview)
- [How AST parsing works](../ARCHITECTURE.md#why-tree-sitter)
- [State model structure](API.md#autodoccorestate)
- [Dependency graph](API.md#autodocanalysisdependency_graph)

**Extend AutoDoc**
- [Development setup](../CONTRIBUTING.md#development-setup)
- [Add a new language](../ARCHITECTURE.md#future-work-phase-4)
- [Implement custom generator](API.md#protocols)
- [Write tests](../CONTRIBUTING.md#testing)

**Troubleshoot Issues**
- [Common problems](EXAMPLES.md#troubleshooting)
- [Large repositories](EXAMPLES.md#16-handling-large-repositories)
- [Corrupted state](EXAMPLES.md#17-fixing-corrupted-state)
- [AST parsing issues](EXAMPLES.md#18-debugging-ast-parsing-issues)

---

## 📖 Documentation by Topic

### Core Concepts

#### State Management
AutoDoc tracks your repository state in `.autodoc/state.json`:
- File hashes (SHA-256) for change detection
- AST hashes for semantic analysis
- Import relationships and dependency graph
- Code definitions (functions, classes, methods)

**Learn more:**
- [State model documentation](../ARCHITECTURE.md#state-model)
- [State API reference](API.md#autodoccorestate)

#### AST Parsing
AutoDoc uses tree-sitter for multi-language code analysis:
- Supports Python, JavaScript, TypeScript
- Extracts functions, classes, and imports
- Detects public vs. private APIs
- Computes stable AST hashes (ignores formatting)

**Learn more:**
- [AST parsing architecture](../ARCHITECTURE.md#why-tree-sitter)
- [AST Parser API](API.md#autodocanalysisast_parser)

#### Dependency Graph
AutoDoc builds a dependency graph from import statements:
- Tracks file-to-file dependencies
- Detects circular dependencies
- Identifies core modules and entry points
- Performs topological sorting

**Learn more:**
- [Dependency graph design](../ARCHITECTURE.md#import-resolution-strategy)
- [Dependency Graph API](API.md#autodocanalysisdependency_graph)

#### Semantic Changes
AutoDoc classifies code changes beyond file diffs:
- **BREAKING**: Removed APIs, signature changes
- **ADDITIVE**: New functions, optional parameters
- **INTERNAL**: Private changes, refactoring
- **DOCS_ONLY**: Documentation updates

**Learn more:**
- [Semantic change detection](../ARCHITECTURE.md#public-vs-private-detection)
- [Semantic Changes API](API.md#autodocanalysissemantic_changes)

### Commands

All CLI commands with detailed explanations:

- [`autodoc init`](API.md#autodoc-init) - Initialize AutoDoc
- [`autodoc scan`](API.md#autodoc-scan) - Scan repository
- [`autodoc generate readme`](API.md#autodoc-generate-readme) - Generate README
- [`autodoc generate resume`](API.md#autodoc-generate-resume) - Generate resume bullets
- [`autodoc watch`](API.md#autodoc-watch) - Watch for changes

### Integrations

AutoDoc integrates with popular tools and workflows:

#### Version Control
- Git repository analysis
- Commit history parsing
- Branch and commit metadata

#### CI/CD Platforms
- [GitHub Actions](EXAMPLES.md#9-github-actions-workflow)
- [GitLab CI](EXAMPLES.md#11-cicd-pipeline-integration)
- [Pre-commit hooks](EXAMPLES.md#10-pre-commit-hook)

#### Documentation Tools
- [MkDocs integration](EXAMPLES.md#20-integrating-with-documentation-sites)
- Sphinx compatibility
- Custom documentation sites

---

## 🎓 Learning Path

### Beginner (Getting Started)

1. Read the [Quick Start](../README.md#-quick-start)
2. Follow [First-Time Setup](EXAMPLES.md#1-first-time-setup) example
3. Try [Updating Documentation](EXAMPLES.md#2-updating-documentation-after-changes)
4. Experiment with [dry-run mode](EXAMPLES.md#7-dry-run-mode-for-testing)

### Intermediate (Customization)

1. Learn [Custom Configuration](EXAMPLES.md#5-custom-configuration)
2. Set up [Watch Mode](EXAMPLES.md#3-continuous-documentation-updates)
3. Configure [GitHub Actions](EXAMPLES.md#9-github-actions-workflow)
4. Explore [Resume Generation](EXAMPLES.md#4-generating-resume-bullets)

### Advanced (Extension)

1. Read [Architecture Documentation](../ARCHITECTURE.md)
2. Understand [API Reference](API.md)
3. Study [Protocol Interfaces](API.md#protocols)
4. Review [Contributing Guide](../CONTRIBUTING.md)

---

## 💡 Tips for Effective Usage

### Documentation Quality

1. **Write good commit messages** - Resume bullets are generated from git history
2. **Use type hints** - Improves API documentation quality in Python
3. **Add docstrings** - AutoDoc can leverage docstrings for descriptions
4. **Keep code organized** - Better structure leads to better generated docs

### Performance

1. **Use `.gitignore` patterns** - AutoDoc respects `.gitignore` by default
2. **Exclude large directories** - Add data/log directories to `exclude_patterns`
3. **Use watch mode during development** - Catches changes immediately
4. **Run incremental scans** - Only changed files are re-analyzed

### Automation

1. **Set up GitHub Actions** - Automate README updates on push
2. **Use pre-commit hooks** - Ensure state is always current
3. **Version your documentation** - Tag README with releases
4. **Review generated content** - Always review before pushing

---

## 🔧 Advanced Topics

### Custom Generators

Implement custom documentation generators using protocols:

```python
from autodoc.core.protocols import Generator

class CustomGenerator(Generator):
    def generate(self, state: dict) -> str:
        # Your custom generation logic
        pass
```

See [API Documentation - Protocols](API.md#protocols) for details.

### Language Support

AutoDoc currently supports Python, JavaScript, and TypeScript. To add more languages:

1. Add tree-sitter grammar for the language
2. Implement language-specific import resolution
3. Add public/private detection rules
4. Update configuration schema

See [Architecture - Future Work](../ARCHITECTURE.md#future-work-phase-4) for roadmap.

### State Schema Evolution

AutoDoc uses versioned state schemas. Current version: 1.1

- **Version 1.0**: Basic file hashes and metadata
- **Version 1.1**: Added AST hashes, imports, definitions, dependency graph

See [Architecture - State Model](../ARCHITECTURE.md#state-model) for schema details.

---

## 🐛 Reporting Issues

Found a bug or have a suggestion? Please report it!

1. **Search existing issues** - Someone might have already reported it
2. **Use issue templates** - Provides necessary information
3. **Include examples** - Minimal reproducible examples help
4. **Share logs** - Use `--verbose` flag and include output

[Open an issue on GitHub](https://github.com/niharo/autodoc/issues/new)

---

## 🤝 Getting Help

- **Documentation** - You're reading it! Use the navigation above
- **Examples** - Check [EXAMPLES.md](EXAMPLES.md) for practical guides
- **API Reference** - See [API.md](API.md) for technical details
- **GitHub Issues** - Search or open an issue
- **GitHub Discussions** - Ask questions and share ideas

---

## 📈 Project Status

AutoDoc is actively maintained and follows semantic versioning.

- **Current Version**: 0.1.0
- **Status**: Alpha (stable, but API may change)
- **Python**: 3.9, 3.10, 3.11, 3.12
- **License**: MIT

See [CHANGELOG.md](../CHANGELOG.md) for release history.

---

**Happy documenting! 📝**

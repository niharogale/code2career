# AutoDoc API Documentation

This document provides detailed API documentation for AutoDoc's core modules and functions.

## Table of Contents

- [CLI Commands](#cli-commands)
- [Core Modules](#core-modules)
- [Analysis Modules](#analysis-modules)
- [Generation Modules](#generation-modules)
- [Exceptions](#exceptions)

---

## CLI Commands

### `autodoc init`

Initialize AutoDoc in a repository.

```bash
autodoc init [OPTIONS]
```

**Options:**
- `--force, -f`: Reinitialize even if `.autodoc/` already exists

**Behavior:**
- Creates `.autodoc/` directory in repository root
- Generates default `config.yaml` with file patterns and settings
- Creates empty `state.json` for tracking repository state
- Fails if `.autodoc/` already exists (unless `--force` is used)

**Example:**
```bash
# Initialize in current repository
autodoc init

# Reinitialize (overwrites existing config)
autodoc init --force
```

---

### `autodoc scan`

Scan repository and detect changes.

```bash
autodoc scan [OPTIONS]
```

**Options:**
- `--verbose, -v`: Show detailed scanning output
- `--dry-run, -n`: Preview changes without saving state

**Behavior:**
- Scans all source files in repository (respecting `.gitignore`)
- Computes SHA-256 hashes for change detection
- Parses AST for supported languages (Python, JavaScript, TypeScript)
- Extracts imports, definitions, and dependencies
- Updates dependency graph
- Classifies files as added/modified/deleted/unchanged
- Updates `.autodoc/state.json` (unless `--dry-run`)

**Example:**
```bash
# Scan repository
autodoc scan

# Scan with detailed output
autodoc scan --verbose

# Preview scan without saving
autodoc scan --dry-run
```

**Output:**
```
Scanning the repository...
Scan completed!
  Total files: 42
  Added: 3
  Modified: 5
  Deleted: 1
  Unchanged: 33
```

---

### `autodoc generate readme`

Generate README based on scan results.

```bash
autodoc generate readme [OPTIONS]
```

**Options:**
- `--output, -o PATH`: Output path for README (default: `README.md` in repo root)
- `--dry-run, -n`: Print README without writing to file
- `--verbose, -v`: Show detailed generation output

**Behavior:**
- Analyzes project type (language, package manager, frameworks)
- Generates README sections: title, description, installation, usage, structure, license
- Uses AST metadata for API documentation
- Leverages dependency graph to identify core modules
- Prompts for confirmation if README exists

**Example:**
```bash
# Generate README
autodoc generate readme

# Preview README without writing
autodoc generate readme --dry-run

# Generate to custom path
autodoc generate readme --output docs/README.md

# Generate with detailed output
autodoc generate readme --verbose
```

---

### `autodoc generate resume`

Generate resume bullets from git history.

```bash
autodoc generate resume [OPTIONS]
```

**Options:**
- `--author, -a NAME`: Filter commits by author name
- `--limit, -l N`: Maximum number of commits to analyze (default: 50)
- `--max, -m N`: Maximum number of bullets to generate (default: 5)
- `--style, -s STYLE`: Output style: `standard`, `detailed`, or `concise` (default: `standard`)
- `--output, -o PATH`: Export to JSON file (optional)
- `--verbose, -v`: Show detailed generation output

**Behavior:**
- Analyzes git commit history
- Extracts semantic changes from commits
- Classifies changes by category (feature, bugfix, refactoring, etc.)
- Generates professional resume bullets
- Formats output based on selected style

**Example:**
```bash
# Generate resume bullets
autodoc generate resume

# Generate for specific author
autodoc generate resume --author "John Doe"

# Generate detailed bullets
autodoc generate resume --style detailed --max 10

# Export to JSON
autodoc generate resume --output resume.json
```

**Output:**
```
--- Resume Bullets ---

• Developed multi-language AST parser supporting Python, JavaScript, and TypeScript using tree-sitter, enabling semantic code analysis across diverse codebases

• Implemented dependency graph analysis system tracking import relationships, detecting circular dependencies, and performing topological sorting for build optimization

• Created semantic change detection engine classifying code modifications as breaking, additive, or internal changes to improve documentation accuracy

--- End Resume Bullets ---
```

---

### `autodoc watch`

Watch repository for changes and automatically update documentation.

```bash
autodoc watch [OPTIONS]
```

**Options:**
- `--interval, -i SECONDS`: Polling interval in seconds (default: 2)
- `--readme / --no-readme`: Auto-generate README on changes (default: enabled)
- `--verbose, -v`: Show detailed output

**Behavior:**
- Watches for file system changes using `watchdog`
- Automatically runs `scan` when files change
- Optionally regenerates README when changes detected
- Runs continuously until interrupted (Ctrl+C)

**Example:**
```bash
# Watch with default settings
autodoc watch

# Watch without auto-generating README
autodoc watch --no-readme

# Watch with custom interval
autodoc watch --interval 5
```

---

## Core Modules

### `autodoc.core.config`

Configuration management with YAML support.

#### `AutodocConfig`

Configuration dataclass with defaults.

```python
from autodoc.core.config import AutodocConfig

# Load from .autodoc/config.yaml
config = AutodocConfig.from_autodoc_dir(Path(".autodoc"))

# Use defaults
config = AutodocConfig.default()

# Access configuration
print(config.include_patterns)  # ['*.py', '*.js', '*.ts', ...]
print(config.exclude_patterns)  # ['.git/**', 'node_modules/**', ...]
print(config.readme_sections)   # ['title', 'description', ...]
```

**Fields:**
- `include_patterns: List[str]` - File patterns to include
- `exclude_patterns: List[str]` - File patterns to exclude
- `readme_sections: List[str]` - README sections to generate
- `verbose: bool` - Enable verbose output (default: False)
- `dry_run: bool` - Enable dry-run mode (default: False)

**Methods:**
- `from_autodoc_dir(path: Path) -> AutodocConfig` - Load from YAML
- `default() -> AutodocConfig` - Create with defaults
- `save(path: Path) -> None` - Save to YAML file

---

### `autodoc.core.state`

State persistence in `.autodoc/state.json`.

#### Functions

```python
from autodoc.core.state import load_state, save_state, get_state_path

# Load state
state = load_state()

# Access state data
files = state["files"]
last_scan = state["last_scan"]
repository = state["repository"]

# Save state
save_state(state)

# Get state file path
path = get_state_path()  # .autodoc/state.json
```

**State Structure (v1.1):**
```python
{
    "version": "1.1",
    "repository": {
        "name": "autodoc",
        "root": "/path/to/repo",
        "branch": "main",
        "commit": "abc123"
    },
    "last_scan": "2026-02-02T12:00:00Z",
    "files": {
        "src/main.py": {
            "hash": "sha256:abc123...",
            "ast_hash": "ast:def456...",
            "language": "python",
            "last_modified": "2026-02-02T11:00:00Z",
            "change_type": "modified",
            "imports": ["os", "sys"],
            "definitions": [
                {
                    "name": "main",
                    "type": "function",
                    "line": 10,
                    "is_public": true
                }
            ]
        }
    },
    "dependency_graph": {
        "nodes": {},
        "dependencies": {},
        "dependents": {}
    }
}
```

---

### `autodoc.core.repository`

Repository context and Git operations.

#### `Repository`

Git repository metadata.

```python
from autodoc.core.repository import Repository

# Create from current directory
repo = Repository.from_cwd()

# Access repository info
print(repo.name)    # Repository name (from git remote or directory name)
print(repo.root)    # Path to repository root
print(repo.branch)  # Current branch name
print(repo.commit)  # Current commit hash (short)

# Enumerate source files
files = repo.enumerate_source_files()  # List[Path]
```

---

### `autodoc.core.scan`

File scanning and change detection.

#### `scan_repository`

Scan repository and detect changes.

```python
from autodoc.core.scan import scan_repository, apply_scan_to_state
from autodoc.core.repository import Repository
from autodoc.core.state import load_state

repo = Repository.from_cwd()
state = load_state()

# Scan repository
result = scan_repository(repo, state)

# Access scan results
print(result.total_files)         # Total files scanned
print(result.added)               # Set of added file paths
print(result.modified)            # Set of modified file paths
print(result.deleted)             # Set of deleted file paths
print(result.unchanged)           # Set of unchanged file paths
print(result.has_changes)         # Boolean: any changes detected
print(result.dependency_graph)    # DependencyGraph instance

# Apply results to state
apply_scan_to_state(state, result, repo, result.dependency_graph)
```

---

## Analysis Modules

### `autodoc.analysis.ast_parser`

Multi-language AST parsing using tree-sitter.

#### `ASTParser`

Abstract Syntax Tree parser for multiple languages.

```python
from autodoc.analysis.ast_parser import ASTParser

parser = ASTParser()

# Parse source code
with open("example.py", "r") as f:
    source_code = f.read()

result = parser.parse("example.py", source_code)

# Access parse results
print(result.language)      # "python"
print(result.imports)       # ["os", "sys", "pathlib"]
print(result.definitions)   # List of Definition objects
print(result.ast_hash)      # Stable AST hash

# Access definitions
for definition in result.definitions:
    print(f"{definition.type} {definition.name} at line {definition.line}")
    print(f"  Public: {definition.is_public}")
```

**Supported Languages:**
- Python (`.py`)
- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)

**Definition Types:**
- `function` - Functions and methods
- `class` - Classes and interfaces
- `method` - Class methods
- `variable` - Module-level variables

---

### `autodoc.analysis.dependency_graph`

Dependency graph for import relationships.

#### `DependencyGraph`

Manages file dependencies based on imports.

```python
from autodoc.analysis.dependency_graph import DependencyGraph

graph = DependencyGraph()

# Add files with their imports
graph.add_file("src/main.py", ["src/utils.py", "src/config.py"])
graph.add_file("src/utils.py", ["src/constants.py"])

# Query dependencies
deps = graph.get_dependencies("src/main.py")  # Direct dependencies
all_deps = graph.get_all_dependencies("src/main.py")  # Transitive

# Query dependents (reverse dependencies)
dependents = graph.get_dependents("src/utils.py")

# Detect circular dependencies
cycles = graph.detect_circular_dependencies()

# Topological sort (build order)
order = graph.topological_sort()

# Identify special nodes
isolated = graph.get_isolated_files()  # No dependencies or dependents
leaves = graph.get_leaf_files()        # No dependencies
roots = graph.get_root_files()         # No dependents

# Serialize/deserialize
data = graph.to_dict()
graph2 = DependencyGraph.from_dict(data)
```

---

### `autodoc.analysis.semantic_changes`

Semantic change classification.

#### `SemanticChangeAnalyzer`

Classifies code changes beyond file hashes.

```python
from autodoc.analysis.semantic_changes import SemanticChangeAnalyzer, ChangeType

analyzer = SemanticChangeAnalyzer()

# Analyze changes between two file versions
old_definitions = [...]  # List of old Definition objects
new_definitions = [...]  # List of new Definition objects

change = analyzer.classify_change(old_definitions, new_definitions)

print(change.type)         # ChangeType.BREAKING, ADDITIVE, INTERNAL, etc.
print(change.description)  # Human-readable description
print(change.details)      # Detailed change information

# Analyze impact on dependent files
dependency_graph = DependencyGraph()
# ... populate graph ...

impact = analyzer.analyze_impact("src/api.py", change, dependency_graph)
print(impact.affected_files)    # List of files affected by change
print(impact.severity)          # Impact severity
```

**Change Types:**
- `ChangeType.BREAKING` - Removed public APIs or signature changes
- `ChangeType.ADDITIVE` - New functions or optional parameters
- `ChangeType.INTERNAL` - Private method changes or refactoring
- `ChangeType.DOCS_ONLY` - Same AST hash, different file hash
- `ChangeType.UNKNOWN` - Unable to classify

---

## Generation Modules

### `autodoc.generation.readme_generator`

README generation with intelligent project analysis.

#### Functions

```python
from autodoc.generation.readme_generator import (
    generate_readme,
    write_readme,
    analyze_project_type
)

# Analyze project type
analysis = analyze_project_type(state)
print(analysis["language"])        # Primary language
print(analysis["package_manager"]) # npm, pip, cargo, etc.
print(analysis["frameworks"])      # List of detected frameworks

# Generate README content
readme_content = generate_readme(state)

# Write README to file
write_readme(repo_root, readme_content)
```

**Detected Project Types:**
- Languages: Python, JavaScript, TypeScript, Rust, Go, Java, C++
- Package Managers: npm, yarn, pip, poetry, cargo, go modules, maven, gradle
- Frameworks: React, Vue, Angular, Django, Flask, FastAPI, Express, Next.js

---

### `autodoc.generation.resume_generator`

Resume bullet generation from commit history.

#### Functions

```python
from autodoc.generation.resume_generator import (
    generate_resume_bullets,
    format_resume_bullets,
    export_resume_bullets_json
)

# Generate resume bullets
bullets = generate_resume_bullets(
    state=state,
    repo_root=repo_root,
    author_filter="John Doe",  # Optional
    limit=50                    # Max commits to analyze
)

# Format bullets
formatted = format_resume_bullets(
    bullets,
    style="standard",  # or "detailed", "concise"
    max_bullets=5
)
print(formatted)

# Export to JSON
json_data = export_resume_bullets_json(bullets)
```

**Bullet Categories:**
- `feature` - New features and capabilities
- `bugfix` - Bug fixes and corrections
- `performance` - Performance improvements
- `refactoring` - Code refactoring and restructuring
- `testing` - Test additions and improvements
- `documentation` - Documentation updates
- `infrastructure` - CI/CD, build, deployment

**Bullet Styles:**
- `standard` - Professional resume format with action verbs
- `detailed` - Extended descriptions with technical details
- `concise` - Short, impactful statements

---

## Exceptions

### Exception Hierarchy

```python
from autodoc.core.exceptions import (
    AutodocError,
    NotInitializedError,
    RepositoryNotFoundError,
    StateCorruptedError,
    ConfigError
)

try:
    # AutoDoc operations
    pass
except NotInitializedError:
    print("Run 'autodoc init' first")
except RepositoryNotFoundError:
    print("Not a git repository")
except StateCorruptedError:
    print("State file is corrupted")
except ConfigError:
    print("Configuration error")
except AutodocError as e:
    print(f"AutoDoc error: {e}")
```

**Exception Types:**
- `AutodocError` - Base exception for all AutoDoc errors
- `NotInitializedError` - `.autodoc/` directory not found
- `RepositoryNotFoundError` - Not in a git repository
- `StateCorruptedError` - Invalid `state.json` file
- `ConfigError` - Malformed `config.yaml`

---

## Protocols

AutoDoc uses typing protocols for extensibility.

```python
from autodoc.core.protocols import (
    StateManager,
    Scanner,
    Generator,
    ConfigLoader,
    Repository as RepositoryProtocol
)

# Implement custom components adhering to protocols
class CustomGenerator(Generator):
    def generate(self, state: dict) -> str:
        # Custom generation logic
        pass
```

**Available Protocols:**
- `StateManager` - State loading/saving operations
- `Scanner` - Repository scanning interface
- `Generator` - Documentation generation
- `ConfigLoader` - Configuration loading
- `Repository` - Repository operations

---

## Type Definitions

### `Definition`

Code definition metadata.

```python
@dataclass
class Definition:
    name: str           # Definition name
    type: str           # function, class, method, variable
    line: int           # Line number where defined
    is_public: bool     # Whether it's part of public API
```

### `ScanResult`

Scan operation results.

```python
@dataclass
class ScanResult:
    total_files: int
    added: Set[str]
    modified: Set[str]
    deleted: Set[str]
    unchanged: Set[str]
    has_changes: bool
    dependency_graph: DependencyGraph
```

### `ParseResult`

AST parsing results.

```python
@dataclass
class ParseResult:
    language: str
    imports: List[str]
    definitions: List[Definition]
    ast_hash: str
```

---

## Configuration File Format

### `.autodoc/config.yaml`

```yaml
# File patterns to include
include_patterns:
  - '*.py'
  - '*.js'
  - '*.ts'
  - '*.jsx'
  - '*.tsx'
  - 'README.*'
  
# File patterns to exclude
exclude_patterns:
  - '.git/**'
  - 'node_modules/**'
  - '__pycache__/**'
  - 'venv/**'
  - '.venv/**'
  - 'dist/**'
  - 'build/**'

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

# AST parsing configuration
ast:
  enabled: true
  languages:
    - python
    - javascript
    - typescript
```

---

## Examples

### Full Workflow Example

```python
from pathlib import Path
from autodoc.core.repository import Repository
from autodoc.core.config import AutodocConfig
from autodoc.core.state import load_state, save_state
from autodoc.core.scan import scan_repository, apply_scan_to_state
from autodoc.generation.readme_generator import generate_readme, write_readme

# 1. Load configuration
config = AutodocConfig.from_autodoc_dir(Path(".autodoc"))

# 2. Get repository context
repo = Repository.from_cwd()

# 3. Load current state
state = load_state()

# 4. Scan repository
scan_result = scan_repository(repo, state)

# 5. Apply scan results
apply_scan_to_state(state, scan_result, repo, scan_result.dependency_graph)

# 6. Save updated state
save_state(state)

# 7. Generate README
readme_content = generate_readme(state)
write_readme(repo.root, readme_content)

print("Documentation updated successfully!")
```

### Custom Parser Example

```python
from autodoc.analysis.ast_parser import ASTParser

parser = ASTParser()

# Parse a Python file
with open("example.py") as f:
    result = parser.parse("example.py", f.read())

# Filter public APIs
public_apis = [d for d in result.definitions if d.is_public]

# Print API summary
for api in public_apis:
    print(f"{api.type} {api.name} (line {api.line})")
```

### Dependency Analysis Example

```python
from autodoc.analysis.dependency_graph import DependencyGraph

# Build dependency graph from state
graph = DependencyGraph.from_dict(state["dependency_graph"])

# Find all files that depend on a core module
core_module = "src/api.py"
dependents = graph.get_all_dependents(core_module)

print(f"Files depending on {core_module}:")
for file in dependents:
    print(f"  - {file}")

# Check for circular dependencies
cycles = graph.detect_circular_dependencies()
if cycles:
    print("Circular dependencies detected:")
    for cycle in cycles:
        print(f"  {' -> '.join(cycle)}")
```

---

## Best Practices

### Performance

1. **Incremental scans**: Only changed files are re-parsed
2. **AST caching**: AST metadata is cached in state file
3. **Lazy loading**: Parse files only when needed
4. **Efficient hashing**: SHA-256 for file changes, custom hash for AST

### Error Handling

```python
from autodoc.core.exceptions import AutodocError

try:
    # AutoDoc operations
    pass
except AutodocError as e:
    # Handle all AutoDoc errors
    logger.error(f"AutoDoc error: {e}")
    # Recover or exit gracefully
```

### Testing

```python
import pytest
from autodoc.core.repository import Repository

def test_repository_detection(tmp_path):
    # Create temporary git repo
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    
    # Initialize git
    import subprocess
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    
    # Test repository creation
    repo = Repository.from_path(repo_dir)
    assert repo.name == "test_repo"
```

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines and how to extend AutoDoc's functionality.

## License

AutoDoc is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

# AutoDoc Usage Examples

This guide provides practical examples for using AutoDoc in various scenarios.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Workflows](#basic-workflows)
- [Advanced Usage](#advanced-usage)
- [Integration Examples](#integration-examples)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Initialize and Generate README

The simplest workflow to generate documentation for your project:

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

## Basic Workflows

### 1. First-Time Setup

**Scenario:** You have an existing project and want to add automated documentation.

```bash
# Step 1: Initialize AutoDoc
autodoc init

# Step 2: Review the generated config (optional)
cat .autodoc/config.yaml

# Step 3: Scan your repository
autodoc scan --verbose

# Step 4: Generate README
autodoc generate readme --dry-run  # Preview first
autodoc generate readme             # Confirm and generate
```

**What happens:**
- `.autodoc/` directory is created with `config.yaml` and `state.json`
- All source files are scanned and analyzed
- AST metadata is extracted for supported languages
- Dependency graph is built
- README is generated based on your project structure

---

### 2. Updating Documentation After Changes

**Scenario:** You've made changes to your code and want to update the documentation.

```bash
# Rescan to detect changes
autodoc scan --verbose

# Regenerate README
autodoc generate readme
```

**Output:**
```
Scanning the repository...
Repository: my-project
Root: /path/to/my-project
Branch: main

Found 3 new files:
  + src/new_feature.py
  + src/utils/helper.py
  + tests/test_new_feature.py

Scan completed!
  Total files: 45
  Added: 3
  Modified: 2
  Deleted: 0
  Unchanged: 40

Changed files:
  [ADDED] src/new_feature.py
  [ADDED] src/utils/helper.py
  [ADDED] tests/test_new_feature.py
  [MODIFIED] src/main.py
  [MODIFIED] README.md
```

---

### 3. Continuous Documentation Updates

**Scenario:** You want AutoDoc to watch for changes and automatically update documentation.

```bash
# Start watch mode
autodoc watch --verbose

# In another terminal, make changes to your code
# AutoDoc will automatically detect changes and update docs
```

**Output:**
```
Watching repository for changes...
Press Ctrl+C to stop

[12:30:45] File modified: src/api.py
[12:30:45] Running scan...
[12:30:46] Scan completed (3 files changed)
[12:30:46] Regenerating README...
[12:30:47] ✓ README updated

[12:35:22] File added: src/new_module.py
[12:35:22] Running scan...
[12:35:23] Scan completed (1 file added)
[12:35:23] Regenerating README...
[12:35:24] ✓ README updated
```

---

### 4. Generating Resume Bullets

**Scenario:** You want to create professional resume bullets from your git history.

```bash
# Generate resume bullets (default: last 50 commits, top 5 bullets)
autodoc generate resume

# Generate more bullets with detailed style
autodoc generate resume --max 10 --style detailed

# Filter by author
autodoc generate resume --author "John Doe" --max 8

# Export to JSON for further processing
autodoc generate resume --output resume.json
```

**Output (Standard Style):**
```
--- Resume Bullets ---

• Developed multi-language AST parser supporting Python, JavaScript, and TypeScript using tree-sitter, enabling semantic code analysis across diverse codebases

• Implemented dependency graph analysis system tracking import relationships, detecting circular dependencies, and performing topological sorting for build optimization

• Created semantic change detection engine classifying code modifications as breaking, additive, or internal changes to improve documentation accuracy

• Built intelligent README generator analyzing project structure, frameworks, and package managers to produce comprehensive documentation automatically

• Designed file watching system using watchdog library providing continuous documentation updates with configurable polling intervals

--- End Resume Bullets ---
```

**Output (Detailed Style):**
```
--- Resume Bullets ---

• Developed multi-language Abstract Syntax Tree (AST) parser supporting Python, JavaScript, and TypeScript using tree-sitter library
  - Implemented language-specific parsers with unified API for cross-language code analysis
  - Extracted function signatures, class definitions, and import statements with public/private API detection
  - Computed stable AST hashes ignoring comments and whitespace for semantic change tracking
  - Achieved 95% accuracy in public API detection using convention-based heuristics

• Implemented comprehensive dependency graph analysis system for tracking file relationships and import dependencies
  - Built bidirectional dependency tracking with transitive closure computation
  - Developed circular dependency detection using depth-first search algorithm
  - Implemented topological sorting for determining optimal build order
  - Created import resolution system handling relative imports, absolute imports, and module paths

--- End Resume Bullets ---
```

---

## Advanced Usage

### 5. Custom Configuration

**Scenario:** You want to customize which files are scanned and which README sections are generated.

**Edit `.autodoc/config.yaml`:**

```yaml
# Include additional file types
include_patterns:
  - '*.py'
  - '*.js'
  - '*.ts'
  - '*.go'      # Add Go files
  - '*.rs'      # Add Rust files
  - 'Makefile'  # Include Makefile
  
# Exclude test directories and build artifacts
exclude_patterns:
  - '.git/**'
  - 'node_modules/**'
  - '__pycache__/**'
  - 'tests/**'      # Exclude tests
  - 'build/**'
  - 'dist/**'
  - '*.test.js'     # Exclude test files

# Customize README sections
readme_sections:
  - title
  - badges           # Add badges section
  - description
  - features         # Add features section
  - installation
  - usage
  - api              # Add API documentation
  - contributing     # Add contributing section
  - license

# Enable verbose output by default
verbose: true
```

**Then rescan:**
```bash
autodoc scan
autodoc generate readme
```

---

### 6. Multi-Language Projects

**Scenario:** Your project uses multiple programming languages.

**Example project structure:**
```
my-fullstack-app/
├── backend/
│   ├── api/
│   │   ├── users.py
│   │   └── auth.py
│   └── models/
│       └── database.py
├── frontend/
│   ├── components/
│   │   ├── App.tsx
│   │   └── Header.tsx
│   └── utils/
│       └── api.ts
└── README.md
```

**Scan and analyze:**
```bash
autodoc init
autodoc scan --verbose
```

**Output:**
```
Scanning the repository...
Scan completed!
  Total files: 24
  Added: 24
  
Languages detected:
  - Python: 8 files
  - TypeScript: 12 files
  - JavaScript: 4 files

Frameworks detected:
  - Backend: Flask
  - Frontend: React
```

**Generated README includes:**
- Installation instructions for both backend and frontend
- API documentation from Python type hints
- Component documentation from TypeScript interfaces
- Dependency information for both ecosystems

---

### 7. Dry-Run Mode for Testing

**Scenario:** You want to preview changes before actually modifying files.

```bash
# Preview scan results without saving
autodoc scan --dry-run --verbose

# Preview README without writing
autodoc generate readme --dry-run
```

**Output:**
```
[DRY RUN] Would save state to .autodoc/state.json

--- Generated README ---

# My Project

A comprehensive Python application for data analysis and visualization.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from myproject import Analyzer

analyzer = Analyzer()
results = analyzer.analyze(data)
```

--- End README ---
```

---

### 8. Analyzing Specific Changes

**Scenario:** You want to understand what changed in your latest commits.

```bash
# Scan to get latest state
autodoc scan --verbose

# Check state file for detailed change information
cat .autodoc/state.json | jq '.files | to_entries | map(select(.value.change_type == "modified")) | .[].key'
```

**Or use Python to analyze:**

```python
import json

with open('.autodoc/state.json') as f:
    state = json.load(f)

# Find modified files
modified = [
    path for path, info in state['files'].items()
    if info.get('change_type') == 'modified'
]

print(f"Modified files: {len(modified)}")
for path in modified:
    file_info = state['files'][path]
    print(f"  {path}")
    print(f"    - Imports: {len(file_info.get('imports', []))}")
    print(f"    - Definitions: {len(file_info.get('definitions', []))}")
```

---

## Integration Examples

### 9. GitHub Actions Workflow

**Scenario:** Automatically update README on every push.

**Create `.github/workflows/autodoc.yml`:**

```yaml
name: Update Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  update-docs:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install AutoDoc
        run: pip install autodoc
      
      - name: Initialize AutoDoc
        run: autodoc init --force
      
      - name: Scan repository
        run: autodoc scan --verbose
      
      - name: Generate README
        run: autodoc generate readme
      
      - name: Commit changes
        if: github.event_name == 'push'
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add README.md .autodoc/
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "docs: update README [skip ci]"
          git push
```

---

### 10. Pre-commit Hook

**Scenario:** Automatically scan changes before each commit.

**Create `.git/hooks/pre-commit`:**

```bash
#!/bin/bash

# Run autodoc scan before committing
echo "Running autodoc scan..."
autodoc scan --verbose

# Check if there are changes to .autodoc/state.json
if git diff --quiet .autodoc/state.json; then
  echo "✓ No documentation changes needed"
else
  echo "✓ Documentation state updated"
  git add .autodoc/state.json
fi

exit 0
```

**Make it executable:**
```bash
chmod +x .git/hooks/pre-commit
```

---

### 11. CI/CD Pipeline Integration

**Scenario:** Validate documentation is up-to-date in CI.

**GitLab CI (`.gitlab-ci.yml`):**

```yaml
stages:
  - test
  - docs

test:
  stage: test
  script:
    - pip install autodoc
    - autodoc init
    - autodoc scan
    - pytest

docs-check:
  stage: docs
  script:
    - pip install autodoc
    - autodoc init --force
    - autodoc scan
    - autodoc generate readme --dry-run > generated-readme.md
    - diff README.md generated-readme.md || (echo "README is out of date" && exit 1)
  only:
    - merge_requests
```

---

## Common Patterns

### 12. Monorepo Setup

**Scenario:** You have multiple projects in a monorepo.

```
monorepo/
├── packages/
│   ├── api/
│   │   ├── .autodoc/
│   │   └── README.md
│   ├── web/
│   │   ├── .autodoc/
│   │   └── README.md
│   └── shared/
│       ├── .autodoc/
│       └── README.md
└── README.md (root)
```

**Script to update all packages:**

```bash
#!/bin/bash
# update-docs.sh

for package in packages/*/; do
  echo "Updating docs for $package"
  cd "$package"
  
  autodoc init --force
  autodoc scan
  autodoc generate readme
  
  cd -
done

echo "✓ All package documentation updated"
```

---

### 13. Custom README Template

**Scenario:** You want to maintain custom sections in your README.

**Strategy:** Use HTML comments to mark AutoDoc sections.

**README.md:**
```markdown
# My Project

This is my custom introduction that AutoDoc won't touch.

## Features

- Custom feature list
- That I maintain manually

<!-- AUTODOC_START:installation -->
<!-- This section is auto-generated by AutoDoc -->
## Installation
...
<!-- AUTODOC_END:installation -->

## My Custom Section

This section is maintained manually.

<!-- AUTODOC_START:api -->
<!-- This section is auto-generated by AutoDoc -->
## API Documentation
...
<!-- AUTODOC_END:api -->
```

---

### 14. Documentation Versioning

**Scenario:** You want to maintain documentation for different versions.

```bash
# Generate docs for current version
autodoc generate readme --output README.md

# Archive for version 1.0
cp README.md docs/v1.0/README.md

# After making v2.0 changes
autodoc scan
autodoc generate readme --output README.md
cp README.md docs/v2.0/README.md
```

---

### 15. Resume Generation for Job Applications

**Scenario:** Generate tailored resume bullets for specific roles.

**For a Backend Role:**
```bash
# Focus on backend commits
autodoc generate resume \
  --author "Your Name" \
  --style detailed \
  --max 8 \
  --output backend-resume.json

# Filter for backend-related commits manually or with jq
jq '.bullets[] | select(.category == "feature" or .category == "performance")' \
  backend-resume.json
```

**For a Full-Stack Role:**
```bash
# Get comprehensive bullets across all areas
autodoc generate resume \
  --author "Your Name" \
  --style standard \
  --max 12 \
  --output fullstack-resume.json
```

---

## Troubleshooting

### 16. Handling Large Repositories

**Scenario:** Your repository has thousands of files and scanning is slow.

**Solution: Exclude unnecessary directories:**

```yaml
# .autodoc/config.yaml
exclude_patterns:
  - '.git/**'
  - 'node_modules/**'
  - 'venv/**'
  - 'data/**'           # Exclude data files
  - 'logs/**'           # Exclude logs
  - 'tmp/**'            # Exclude temporary files
  - '*.min.js'          # Exclude minified files
  - 'dist/**'
  - 'build/**'
```

**Alternative: Scan incrementally:**
```bash
# Only scan changed files
autodoc scan --verbose

# The state file tracks unchanged files, so rescanning is fast
```

---

### 17. Fixing Corrupted State

**Scenario:** Your `.autodoc/state.json` is corrupted.

**Solution: Reinitialize:**

```bash
# Backup old state (optional)
cp .autodoc/state.json .autodoc/state.json.backup

# Reinitialize
autodoc init --force

# Rescan from scratch
autodoc scan --verbose
```

---

### 18. Debugging AST Parsing Issues

**Scenario:** AutoDoc isn't detecting functions/classes correctly.

**Solution: Check with verbose mode:**

```bash
autodoc scan --verbose --dry-run
```

**Manually inspect state:**
```python
import json

with open('.autodoc/state.json') as f:
    state = json.load(f)

# Check a specific file
file_info = state['files']['src/my_file.py']
print(f"Definitions found: {len(file_info['definitions'])}")
for defn in file_info['definitions']:
    print(f"  {defn['type']} {defn['name']} (line {defn['line']})")
```

---

### 19. Working with Non-Git Repositories

**Scenario:** You want to use AutoDoc on a project that's not in Git.

**Current limitation:** AutoDoc requires a Git repository for many features.

**Workaround:**
```bash
# Initialize git (even if you don't use it)
git init
git add .
git commit -m "Initial commit"

# Now AutoDoc will work
autodoc init
autodoc scan
```

---

### 20. Integrating with Documentation Sites

**Scenario:** You use a documentation generator (Sphinx, MkDocs, etc.).

**MkDocs Example:**

```yaml
# mkdocs.yml
site_name: My Project
nav:
  - Home: README.md          # Generated by AutoDoc
  - API: docs/API.md         # Can also be generated
  - Examples: docs/EXAMPLES.md

plugins:
  - search
```

**Build process:**
```bash
# Update AutoDoc documentation
autodoc scan
autodoc generate readme

# Build MkDocs site
mkdocs build

# Or serve locally
mkdocs serve
```

---

## Tips and Best Practices

### Performance Tips

1. **Use `.gitignore` patterns**: AutoDoc respects `.gitignore` by default
2. **Exclude large data directories**: Add to `exclude_patterns` in config
3. **Use watch mode during development**: Catches changes immediately
4. **Run scans incrementally**: Only changed files are re-analyzed

### Documentation Quality Tips

1. **Write good commit messages**: Resume bullets are generated from git history
2. **Use type hints**: Improves API documentation quality
3. **Add docstrings**: AutoDoc can leverage docstrings for descriptions
4. **Keep code organized**: Better structure = better generated docs

### Automation Tips

1. **Set up GitHub Actions**: Automate README updates
2. **Use pre-commit hooks**: Ensure state is always current
3. **Version your documentation**: Tag README with releases
4. **Review generated content**: Always review before pushing

---

## Next Steps

- Read the [API Documentation](API.md) for programmatic usage
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for extending AutoDoc
- See [ARCHITECTURE.md](../ARCHITECTURE.md) for technical details

---

**Questions or Issues?** Open an issue on [GitHub](https://github.com/niharo/autodoc/issues).

# autodoc/generation/readme_generator.py
"""
README generation module - produces and updates README.md files.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import re

from autodoc.analysis.dependency_graph import DependencyGraph


@dataclass
class ReadmeSection:
    """Represents a section of the README."""
    name: str
    title: str
    content: str
    source_files: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert section to markdown format."""
        return f"## {self.title}\n\n{self.content}\n"


@dataclass
class ReadmeTemplate:
    """Template for generating a README."""
    sections: List[ReadmeSection] = field(default_factory=list)
    
    def to_markdown(self, repo_name: str) -> str:
        """Generate complete README markdown."""
        lines = [f"# {repo_name}\n"]
        
        for section in self.sections:
            lines.append(section.to_markdown())
        
        return "\n".join(lines)


def load_dependency_graph(state: Dict[str, Any]) -> Optional[DependencyGraph]:
    """
    Load the dependency graph from state.
    
    Args:
        state: The autodoc state dictionary
        
    Returns:
        DependencyGraph instance or None if not available
    """
    graph_data = state.get("dependency_graph", {})
    if not graph_data:
        return None
    
    try:
        return DependencyGraph.from_dict(graph_data)
    except Exception:
        return None


def identify_core_files(
    files: Dict[str, Any], 
    dep_graph: Optional[DependencyGraph]
) -> Set[str]:
    """
    Identify core/central files based on dependency relationships.
    
    Core files are those that:
    - Have many dependents (are imported by many files)
    - Are not in test directories
    - Have public APIs (based on definitions)
    
    Args:
        files: Files dictionary from state
        dep_graph: Dependency graph
        
    Returns:
        Set of core file paths
    """
    if not dep_graph:
        return set()
    
    core_files = set()
    
    for path in files.keys():
        # Skip test files
        if "test" in path.lower() or "spec" in path.lower():
            continue
        
        # Files with many dependents are core
        dependents = dep_graph.get_dependents(path)
        if len(dependents) >= 3:
            core_files.add(path)
    
    return core_files


def categorize_files_by_role(
    files: Dict[str, Any],
    dep_graph: Optional[DependencyGraph]
) -> Dict[str, List[str]]:
    """
    Categorize files by their role in the codebase.
    
    Categories:
    - entry_points: Files with no dependents (entry points)
    - core: Highly connected files (utilities, base classes)
    - tests: Test files
    - config: Configuration files
    - docs: Documentation files
    
    Args:
        files: Files dictionary from state
        dep_graph: Dependency graph
        
    Returns:
        Dictionary mapping category to list of file paths
    """
    categories: Dict[str, List[str]] = {
        "entry_points": [],
        "core": [],
        "tests": [],
        "config": [],
        "docs": [],
        "other": []
    }
    
    core_files = identify_core_files(files, dep_graph)
    
    for path, info in files.items():
        basename = Path(path).name.lower()
        
        # Documentation files
        if any(basename.startswith(prefix) for prefix in ["readme", "changelog", "contributing", "license"]):
            categories["docs"].append(path)
        
        # Configuration files
        elif any(basename == name for name in [
            "pyproject.toml", "package.json", "cargo.toml", "go.mod",
            "requirements.txt", "setup.py", "setup.cfg", "config.yaml"
        ]):
            categories["config"].append(path)
        
        # Test files
        elif "test" in path.lower() or "spec" in path.lower():
            categories["tests"].append(path)
        
        # Core files (highly connected)
        elif path in core_files:
            categories["core"].append(path)
        
        # Entry points (leaf nodes with no dependents)
        elif dep_graph and not dep_graph.get_dependents(path) and dep_graph.get_dependencies(path):
            categories["entry_points"].append(path)
        
        # Other
        else:
            categories["other"].append(path)
    
    return categories


def extract_public_api(files: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract public API elements from files based on AST definitions.
    
    Returns dict mapping file path to list of public definitions (classes, functions).
    Only includes definitions that appear to be public (not starting with _).
    
    Args:
        files: Files dictionary from state with AST metadata
        
    Returns:
        Dictionary mapping file paths to public API definitions
    """
    public_apis: Dict[str, List[Dict[str, Any]]] = {}
    
    for path, info in files.items():
        definitions = info.get("definitions", [])
        if not definitions:
            continue
        
        # Filter to public definitions (not starting with _)
        public_defs = [
            d for d in definitions
            if not d.get("name", "").startswith("_")
        ]
        
        if public_defs:
            public_apis[path] = public_defs
    
    return public_apis


def analyze_project_type(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the project type based on files in state.
    
    Returns dict with:
        - language: Primary language
        - frameworks: Detected frameworks
        - package_manager: Detected package manager
        - has_tests: Whether tests were detected
        - dependency_graph: Loaded dependency graph
        - core_files: Core/central files
        - file_categories: Files categorized by role
        - public_apis: Public API elements
    """
    files = state.get("files", {})
    file_paths = list(files.keys())
    
    # Load dependency graph
    dep_graph = load_dependency_graph(state)
    
    analysis = {
        "language": "unknown",
        "frameworks": [],
        "package_manager": None,
        "has_tests": False,
        "entry_points": [],
        "dependency_graph": dep_graph,
        "core_files": identify_core_files(files, dep_graph),
        "file_categories": categorize_files_by_role(files, dep_graph),
        "public_apis": extract_public_api(files),
    }
    
    # Count languages
    lang_counts: Dict[str, int] = {}
    for path, info in files.items():
        lang = info.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    if lang_counts:
        analysis["language"] = max(lang_counts, key=lang_counts.get)
    
    # Detect package manager and frameworks
    for path in file_paths:
        basename = Path(path).name
        
        # Python
        if basename == "pyproject.toml":
            analysis["package_manager"] = "pip/poetry"
        elif basename == "requirements.txt":
            analysis["package_manager"] = analysis["package_manager"] or "pip"
        elif basename == "setup.py":
            analysis["package_manager"] = analysis["package_manager"] or "pip"
        
        # JavaScript/TypeScript
        elif basename == "package.json":
            analysis["package_manager"] = "npm/yarn"
        
        # Rust
        elif basename == "Cargo.toml":
            analysis["package_manager"] = "cargo"
        
        # Go
        elif basename == "go.mod":
            analysis["package_manager"] = "go modules"
        
        # Tests
        if "test" in path.lower() or "spec" in path.lower():
            analysis["has_tests"] = True
        
        # Entry points
        if basename in ("main.py", "app.py", "index.js", "index.ts", "main.go", "main.rs"):
            analysis["entry_points"].append(path)
    
    return analysis


def generate_overview_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> ReadmeSection:
    """Generate the overview/description section."""
    repo_name = state.get("repo", {}).get("name", "Project")
    language = analysis.get("language", "unknown")
    
    content = f"A {language} project."
    
    if analysis.get("frameworks"):
        frameworks = ", ".join(analysis["frameworks"])
        content += f" Built with {frameworks}."
    
    return ReadmeSection(
        name="overview",
        title="Overview",
        content=content
    )


def generate_installation_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> ReadmeSection:
    """Generate the installation section based on detected package manager."""
    package_manager = analysis.get("package_manager")
    language = analysis.get("language", "unknown")
    repo_name = state.get("repo", {}).get("name", "project")
    
    lines = []
    
    if package_manager == "pip/poetry":
        lines.extend([
            "```bash",
            "# Clone the repository",
            f"git clone https://github.com/username/{repo_name}.git",
            f"cd {repo_name}",
            "",
            "# Install dependencies",
            "pip install -e .",
            "```"
        ])
    elif package_manager == "pip":
        lines.extend([
            "```bash",
            "# Clone the repository",
            f"git clone https://github.com/username/{repo_name}.git",
            f"cd {repo_name}",
            "",
            "# Install dependencies",
            "pip install -r requirements.txt",
            "```"
        ])
    elif package_manager == "npm/yarn":
        lines.extend([
            "```bash",
            "# Clone the repository",
            f"git clone https://github.com/username/{repo_name}.git",
            f"cd {repo_name}",
            "",
            "# Install dependencies",
            "npm install",
            "```"
        ])
    elif package_manager == "cargo":
        lines.extend([
            "```bash",
            "# Clone the repository",
            f"git clone https://github.com/username/{repo_name}.git",
            f"cd {repo_name}",
            "",
            "# Build the project",
            "cargo build --release",
            "```"
        ])
    elif package_manager == "go modules":
        lines.extend([
            "```bash",
            "# Clone the repository",
            f"git clone https://github.com/username/{repo_name}.git",
            f"cd {repo_name}",
            "",
            "# Build the project",
            "go build",
            "```"
        ])
    else:
        lines.extend([
            "```bash",
            "# Clone the repository",
            f"git clone https://github.com/username/{repo_name}.git",
            f"cd {repo_name}",
            "```"
        ])
    
    return ReadmeSection(
        name="installation",
        title="Installation",
        content="\n".join(lines),
        source_files=["pyproject.toml", "requirements.txt", "package.json", "Cargo.toml", "go.mod"]
    )


def generate_usage_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> ReadmeSection:
    """Generate the usage section."""
    repo_name = state.get("repo", {}).get("name", "project")
    entry_points = analysis.get("entry_points", [])
    language = analysis.get("language", "unknown")
    
    lines = []
    
    if entry_points:
        main_entry = entry_points[0]
        if language == "python":
            lines.extend([
                "```bash",
                f"python {main_entry}",
                "```"
            ])
        elif language in ("javascript", "typescript"):
            lines.extend([
                "```bash",
                f"node {main_entry}",
                "```"
            ])
        elif language == "go":
            lines.extend([
                "```bash",
                f"go run {main_entry}",
                "```"
            ])
        elif language == "rust":
            lines.extend([
                "```bash",
                "cargo run",
                "```"
            ])
    else:
        lines.append("<!-- Add usage instructions here -->")
    
    return ReadmeSection(
        name="usage",
        title="Usage",
        content="\n".join(lines),
        source_files=entry_points
    )


def generate_structure_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> ReadmeSection:
    """Generate the project structure section."""
    files = state.get("files", {})
    file_categories = analysis.get("file_categories", {})
    core_files = analysis.get("core_files", set())
    
    # Group files by top-level directory
    structure: Dict[str, List[str]] = {}
    for path in sorted(files.keys()):
        parts = Path(path).parts
        if len(parts) > 1:
            top_dir = parts[0]
            if top_dir not in structure:
                structure[top_dir] = []
            structure[top_dir].append(path)
        else:
            if "_root" not in structure:
                structure["_root"] = []
            structure["_root"].append(path)
    
    lines = ["```"]
    
    # Show root files first
    if "_root" in structure:
        for f in structure["_root"][:5]:  # Limit to 5 root files
            marker = " (core)" if f in core_files else ""
            lines.append(f"├── {f}{marker}")
        del structure["_root"]
    
    # Show directories with more context
    for dir_name, dir_files in sorted(structure.items()):
        # Count core files in this directory
        core_count = sum(1 for f in dir_files if f in core_files)
        dir_marker = f" ({core_count} core files)" if core_count > 0 else ""
        lines.append(f"├── {dir_name}/{dir_marker}")
        
        for f in dir_files[:3]:  # Limit to 3 files per directory
            rel = str(Path(f).relative_to(dir_name)) if "/" in f else f
            marker = " (core)" if f in core_files else ""
            lines.append(f"│   ├── {rel}{marker}")
        if len(dir_files) > 3:
            lines.append(f"│   └── ... ({len(dir_files) - 3} more files)")
    
    lines.append("```")
    
    # Add explanation of categories if we have dependency data
    if file_categories and any(file_categories.values()):
        lines.extend([
            "",
            "**Key Components:**",
            ""
        ])
        
        if file_categories.get("core"):
            lines.append(f"- **Core files**: {len(file_categories['core'])} central modules")
        if file_categories.get("entry_points"):
            lines.append(f"- **Entry points**: {len(file_categories['entry_points'])} executable files")
        if file_categories.get("tests"):
            lines.append(f"- **Tests**: {len(file_categories['tests'])} test files")
    
    return ReadmeSection(
        name="structure",
        title="Project Structure",
        content="\n".join(lines),
        source_files=list(files.keys())
    )


def generate_architecture_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[ReadmeSection]:
    """
    Generate an architecture section based on dependency graph analysis.
    
    Args:
        state: The autodoc state dictionary
        analysis: Project analysis results
        
    Returns:
        ReadmeSection with architecture insights or None
    """
    dep_graph = analysis.get("dependency_graph")
    core_files = analysis.get("core_files", set())
    file_categories = analysis.get("file_categories", {})
    
    if not dep_graph:
        return None
    
    lines = []
    lines.append("This section provides insights into the codebase architecture based on dependency analysis.")
    lines.append("")
    
    # Detect circular dependencies
    cycles = dep_graph.detect_cycles()
    if cycles:
        lines.append("### Circular Dependencies Detected")
        lines.append("")
        lines.append(f"Found {len(cycles)} circular dependency chain(s):")
        lines.append("")
        for i, cycle in enumerate(cycles[:3], 1):  # Show first 3
            cycle_str = " → ".join([Path(f).name for f in cycle[:5]])
            if len(cycle) > 5:
                cycle_str += " → ..."
            lines.append(f"{i}. {cycle_str}")
        lines.append("")
        if len(cycles) > 3:
            lines.append(f"*...and {len(cycles) - 3} more*")
            lines.append("")
    
    # Show core modules
    if core_files:
        lines.append("### Core Modules")
        lines.append("")
        lines.append("These modules are central to the codebase (imported by many files):")
        lines.append("")
        
        # Sort by number of dependents
        core_with_deps = []
        for path in core_files:
            dep_count = len(dep_graph.get_dependents(path))
            core_with_deps.append((path, dep_count))
        
        core_with_deps.sort(key=lambda x: x[1], reverse=True)
        
        for path, dep_count in core_with_deps[:10]:  # Top 10
            lines.append(f"- `{path}` (imported by {dep_count} files)")
        lines.append("")
    
    # Show entry points
    entry_points = file_categories.get("entry_points", [])
    if entry_points:
        lines.append("### Entry Points")
        lines.append("")
        lines.append("These files serve as entry points (not imported by other files):")
        lines.append("")
        for path in entry_points[:5]:  # Show first 5
            lines.append(f"- `{path}`")
        lines.append("")
    
    # Show isolated files
    isolated = dep_graph.get_isolated_files()
    if isolated:
        lines.append("### Isolated Files")
        lines.append("")
        lines.append(f"{len(isolated)} file(s) have no dependencies and are not imported by other files.")
        lines.append("")
    
    return ReadmeSection(
        name="architecture",
        title="Architecture",
        content="\n".join(lines),
        source_files=[]
    )


def generate_changes_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[ReadmeSection]:
    """
    Generate a section highlighting recent changes with semantic categorization.
    
    Args:
        state: The autodoc state dictionary
        analysis: Project analysis results
        
    Returns:
        ReadmeSection with change summary or None if no relevant changes
    """
    files = state.get("files", {})
    
    # Group files by semantic category
    breaking_changes = []
    additive_changes = []
    internal_changes = []
    
    for path, info in files.items():
        semantic_category = info.get("semantic_category")
        change_type = info.get("change_type")
        
        if not semantic_category or change_type not in ["added", "modified"]:
            continue
        
        if semantic_category == "breaking":
            breaking_changes.append(path)
        elif semantic_category == "additive":
            additive_changes.append(path)
        elif semantic_category == "internal":
            internal_changes.append(path)
    
    # Only generate section if we have categorized changes
    if not (breaking_changes or additive_changes or internal_changes):
        return None
    
    lines = []
    
    if breaking_changes:
        lines.append("### Breaking Changes")
        lines.append("")
        lines.append("The following files contain breaking API changes:")
        lines.append("")
        for path in breaking_changes[:10]:  # Limit to 10
            lines.append(f"- `{path}`")
        lines.append("")
    
    if additive_changes:
        lines.append("### New Features")
        lines.append("")
        lines.append("The following files contain new functionality:")
        lines.append("")
        for path in additive_changes[:10]:  # Limit to 10
            lines.append(f"- `{path}`")
        lines.append("")
    
    if internal_changes:
        lines.append("### Internal Changes")
        lines.append("")
        lines.append(f"{len(internal_changes)} files have internal implementation changes without API modifications.")
        lines.append("")
    
    return ReadmeSection(
        name="recent_changes",
        title="Recent Changes",
        content="\n".join(lines),
        source_files=breaking_changes + additive_changes
    )


def generate_api_section(state: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[ReadmeSection]:
    """
    Generate API reference section based on AST definitions.
    
    Args:
        state: The autodoc state dictionary
        analysis: Project analysis results
        
    Returns:
        ReadmeSection with API documentation or None if no public APIs found
    """
    public_apis = analysis.get("public_apis", {})
    core_files = analysis.get("core_files", set())
    
    if not public_apis:
        return None
    
    lines = []
    lines.append("This section provides an overview of the public API based on code analysis.")
    lines.append("")
    
    # Prioritize core files
    api_files = sorted(public_apis.keys(), key=lambda p: (p not in core_files, p))
    
    # Group by top-level module/directory
    modules: Dict[str, List[tuple]] = {}
    for path in api_files:
        parts = Path(path).parts
        if len(parts) > 1:
            module = parts[0]
        else:
            module = "_root"
        
        if module not in modules:
            modules[module] = []
        modules[module].append((path, public_apis[path]))
    
    # Generate API documentation by module
    for module_name, module_files in sorted(modules.items()):
        if module_name == "_root":
            lines.append("### Root Level")
        else:
            lines.append(f"### {module_name}")
        lines.append("")
        
        for path, definitions in module_files[:5]:  # Limit to 5 files per module
            # Show file path
            lines.append(f"**`{path}`**")
            
            is_core = path in core_files
            if is_core:
                lines.append("*(core module)*")
            
            lines.append("")
            
            # Show public classes and functions
            classes = [d for d in definitions if d.get("type") == "class"]
            functions = [d for d in definitions if d.get("type") == "function"]
            
            if classes:
                lines.append("Classes:")
                for cls in classes[:5]:  # Limit to 5 classes
                    lines.append(f"- `{cls.get('name')}`")
                lines.append("")
            
            if functions:
                lines.append("Functions:")
                for func in functions[:5]:  # Limit to 5 functions
                    lines.append(f"- `{func.get('name')}`")
                lines.append("")
        
        if len(module_files) > 5:
            lines.append(f"*...and {len(module_files) - 5} more files*")
            lines.append("")
    
    return ReadmeSection(
        name="api",
        title="API Reference",
        content="\n".join(lines),
        source_files=list(public_apis.keys())
    )


def generate_readme(state: Dict[str, Any], include_advanced_sections: bool = True) -> str:
    """
    Generate a complete README based on the current state.
    
    Args:
        state: The autodoc state dictionary
        include_advanced_sections: Whether to include API, architecture, and changes sections
        
    Returns:
        Complete README markdown content
    """
    repo_info = state.get("repo", {})
    repo_name = repo_info.get("name", "Project")
    
    # Analyze project
    analysis = analyze_project_type(state)
    
    # Build template with sections
    template = ReadmeTemplate()
    
    template.sections.append(generate_overview_section(state, analysis))
    template.sections.append(generate_installation_section(state, analysis))
    template.sections.append(generate_usage_section(state, analysis))
    template.sections.append(generate_structure_section(state, analysis))
    
    # Add advanced sections based on AST and dependency data
    if include_advanced_sections:
        # Add architecture section if we have dependency graph
        arch_section = generate_architecture_section(state, analysis)
        if arch_section:
            template.sections.append(arch_section)
        
        # Add API section if we have AST data
        api_section = generate_api_section(state, analysis)
        if api_section:
            template.sections.append(api_section)
        
        # Add recent changes section if we have semantic analysis
        changes_section = generate_changes_section(state, analysis)
        if changes_section:
            template.sections.append(changes_section)
    
    # Add license section placeholder
    template.sections.append(ReadmeSection(
        name="license",
        title="License",
        content="<!-- Add license information here -->"
    ))
    
    return template.to_markdown(repo_name)


def merge_readme(existing_content: str, new_sections: Dict[str, ReadmeSection]) -> str:
    """
    Merge new sections into an existing README, preserving manual edits
    in sections not being updated.
    
    Args:
        existing_content: Current README content
        new_sections: Dict of section name -> ReadmeSection to update
        
    Returns:
        Merged README content
    """
    # Simple implementation: for now, just return the new content
    # Future: parse existing README and merge intelligently
    
    # Find section boundaries in existing content
    section_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
    
    # For now, if we have existing content, preserve it
    # Only add sections that don't exist
    if existing_content.strip():
        result = existing_content
        for name, section in new_sections.items():
            section_header = f"## {section.title}"
            if section_header not in existing_content:
                result += f"\n{section.to_markdown()}"
        return result
    
    # No existing content, generate from new sections
    lines = []
    for section in new_sections.values():
        lines.append(section.to_markdown())
    return "\n".join(lines)


def write_readme(repo_root: Path, content: str) -> Path:
    """
    Write README content to the repository.
    
    Args:
        repo_root: Path to repository root
        content: README markdown content
        
    Returns:
        Path to the written README file
    """
    readme_path = repo_root / "README.md"
    readme_path.write_text(content, encoding="utf-8")
    return readme_path

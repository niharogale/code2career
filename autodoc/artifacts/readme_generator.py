# autodoc/artifacts/readme_generator.py
"""
README generation module - produces and updates README.md files.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import re


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


def analyze_project_type(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the project type based on files in state.
    
    Returns dict with:
        - language: Primary language
        - frameworks: Detected frameworks
        - package_manager: Detected package manager
        - has_tests: Whether tests were detected
    """
    files = state.get("files", {})
    file_paths = list(files.keys())
    
    analysis = {
        "language": "unknown",
        "frameworks": [],
        "package_manager": None,
        "has_tests": False,
        "entry_points": []
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
            lines.append(f"├── {f}")
        del structure["_root"]
    
    # Show directories
    for dir_name, dir_files in sorted(structure.items()):
        lines.append(f"├── {dir_name}/")
        for f in dir_files[:3]:  # Limit to 3 files per directory
            rel = str(Path(f).relative_to(dir_name)) if "/" in f else f
            lines.append(f"│   ├── {rel}")
        if len(dir_files) > 3:
            lines.append(f"│   └── ... ({len(dir_files) - 3} more files)")
    
    lines.append("```")
    
    return ReadmeSection(
        name="structure",
        title="Project Structure",
        content="\n".join(lines),
        source_files=list(files.keys())
    )


def generate_readme(state: Dict[str, Any]) -> str:
    """
    Generate a complete README based on the current state.
    
    Args:
        state: The autodoc state dictionary
        
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

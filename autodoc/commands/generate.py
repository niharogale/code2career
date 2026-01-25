import typer
from pathlib import Path

from autodoc.core.repository import Repository
from autodoc.core.state import get_state_path, load_state
from autodoc.core.config import AutodocConfig
from autodoc.core.exceptions import NotInitializedError, RepositoryNotFoundError
from autodoc.generation.readme_generator import generate_readme, write_readme, analyze_project_type

app = typer.Typer(
    help="Generate README and resume based on the scan results"
)


@app.command()
def readme(
    output: str = typer.Option(None, "--output", "-o", help="Output path for README (default: README.md in repo root)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Print README without writing to file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed generation output"),
):
    """
    Generate README based on the scan results.
    """
    autodoc_dir = get_state_path().parent

    if not autodoc_dir.exists():
        raise NotInitializedError()
    
    # Load configuration
    try:
        config = AutodocConfig.from_autodoc_dir(autodoc_dir)
        config.verbose = verbose or config.verbose
        config.dry_run = dry_run or config.dry_run
    except Exception as e:
        typer.echo(f"Warning: Could not load config, using defaults: {e}")
        config = AutodocConfig.default()
        config.verbose = verbose
        config.dry_run = dry_run
    
    # Load state
    state = load_state()
    
    if not state.get("files"):
        typer.echo("No files in state. Please run 'autodoc scan' first.")
        raise typer.Exit(code=1)
    
    if config.verbose:
        typer.echo(f"Loaded state with {len(state.get('files', {}))} files")
        analysis = analyze_project_type(state)
        typer.echo(f"Detected language: {analysis.get('language', 'unknown')}")
        typer.echo(f"Package manager: {analysis.get('package_manager', 'none')}")
    
    typer.echo("Generating README...")
    
    # Generate README content
    readme_content = generate_readme(state)
    
    if config.verbose:
        typer.echo(f"Generated README with {len(readme_content)} characters")
    
    if config.dry_run:
        typer.echo("\n--- Generated README ---\n")
        typer.echo(readme_content)
        typer.echo("\n--- End README ---")
        return
    
    # Determine output path
    try:
        repo = Repository.from_cwd()
        repo_root = repo.root
    except ValueError as e:
        if config.verbose:
            typer.echo(f"Not in a git repository, using current directory: {e}")
        repo_root = Path.cwd()
    
    if output:
        output_path = Path(output)
    else:
        output_path = repo_root / "README.md"
    
    # Check if README exists and warn
    if output_path.exists():
        typer.confirm(
            f"README already exists at {output_path}. Overwrite?",
            abort=True
        )
    
    # Write README
    write_readme(output_path.parent, readme_content)
    typer.echo(f"✓ README generated at {output_path}")
    
    if config.verbose:
        typer.echo(f"File size: {len(readme_content)} bytes")


@app.command()
def resume():
    """
    Generate resume bullets based on the scan results.
    """
    autodoc_dir = get_state_path().parent

    if not autodoc_dir.exists():
        typer.echo("AutoDoc is not initialized in this repository. Please run 'autodoc init' first.")
        raise typer.Exit(code=1)
    
    # Load state
    state = load_state()
    
    if not state.get("files"):
        typer.echo("No files in state. Please run 'autodoc scan' first.")
        raise typer.Exit(code=1)
    
    typer.echo("Generating resume bullets...")
    
    # For now, generate simple bullet points from project analysis
    repo_info = state.get("repo", {})
    repo_name = repo_info.get("name", "Project")
    files = state.get("files", {})
    
    # Count languages
    lang_counts = {}
    for info in files.values():
        lang = info.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    primary_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "code"
    total_files = len(files)
    
    typer.echo("\n--- Resume Bullets ---\n")
    typer.echo(f"• Developed {repo_name}, a {primary_lang} project with {total_files} source files")
    
    if lang_counts:
        langs = ", ".join(sorted(lang_counts.keys()))
        typer.echo(f"• Technologies used: {langs}")
    
    typer.echo("\n--- End Resume Bullets ---")
    typer.echo("\nNote: Resume generation is a placeholder. Full implementation coming in a future phase.")

import typer
from pathlib import Path

from autodoc.core.repository import Repository
from autodoc.core.state import get_state_path, load_state
from autodoc.core.config import AutodocConfig
from autodoc.core.exceptions import NotInitializedError, RepositoryNotFoundError
from autodoc.generation.readme_generator import generate_readme, write_readme, analyze_project_type
from autodoc.generation.resume_generator import (
    generate_resume_bullets,
    format_resume_bullets,
    export_resume_bullets_json
)

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
def resume(
    author: str = typer.Option(None, "--author", "-a", help="Filter commits by author name"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of commits to analyze"),
    max_bullets: int = typer.Option(5, "--max", "-m", help="Maximum number of bullets to generate"),
    style: str = typer.Option("standard", "--style", "-s", help="Output style: standard, detailed, or concise"),
    output: str = typer.Option(None, "--output", "-o", help="Output JSON file path (optional)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed generation output"),
):
    """
    Generate resume bullets based on git history and semantic changes.
    """
    autodoc_dir = get_state_path().parent

    if not autodoc_dir.exists():
        raise NotInitializedError()
    
    # Load configuration
    try:
        config = AutodocConfig.from_autodoc_dir(autodoc_dir)
        config.verbose = verbose or config.verbose
    except Exception as e:
        if verbose:
            typer.echo(f"Warning: Could not load config, using defaults: {e}")
        config = AutodocConfig.default()
        config.verbose = verbose
    
    # Load state
    state = load_state()
    
    if not state.get("files"):
        typer.echo("No files in state. Please run 'autodoc scan' first.")
        raise typer.Exit(code=1)
    
    # Get repository root
    try:
        repo = Repository.from_cwd()
        repo_root = repo.root
    except ValueError as e:
        typer.echo(f"Error: Not in a git repository: {e}")
        raise typer.Exit(code=1)
    
    if config.verbose:
        typer.echo(f"Analyzing git history (limit: {limit} commits)...")
        if author:
            typer.echo(f"Filtering by author: {author}")
    
    typer.echo("Generating resume bullets...")
    
    # Generate resume bullets
    bullets = generate_resume_bullets(
        state=state,
        repo_root=repo_root,
        author_filter=author,
        limit=limit
    )
    
    if not bullets:
        typer.echo("No resume bullets could be generated. Make sure you have git commits in this repository.")
        raise typer.Exit(code=1)
    
    if config.verbose:
        typer.echo(f"Generated {len(bullets)} bullets")
    
    # Format and display bullets
    formatted = format_resume_bullets(bullets, style=style, max_bullets=max_bullets)
    
    typer.echo("\n--- Resume Bullets ---\n")
    typer.echo(formatted)
    typer.echo("\n--- End Resume Bullets ---")
    
    # Export to JSON if requested
    if output:
        import json
        output_path = Path(output)
        export_data = export_resume_bullets_json(bullets)
        
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        typer.echo(f"\n✓ Resume bullets exported to {output_path}")
    
    if config.verbose:
        typer.echo(f"\nTotal bullets generated: {len(bullets)}")
        typer.echo(f"Displayed: {min(max_bullets, len(bullets))}")
        
        # Show category breakdown
        categories = {}
        for bullet in bullets:
            categories[bullet.category] = categories.get(bullet.category, 0) + 1
        
        typer.echo("\nCategory breakdown:")
        for category, count in sorted(categories.items()):
            typer.echo(f"  {category}: {count}")

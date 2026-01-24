import typer
from pathlib import Path

from autodoc.core.state import default_state, save_state, get_state_path
from autodoc.core.config import AutodocConfig
from autodoc.core.exceptions import NotInitializedError

app = typer.Typer(
    help="Initialize AutoDoc configuration in the repository"
)


@app.callback(invoke_without_command=True)
def init(
    ctx: typer.Context,
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Reinitialize even if .autodoc/ already exists"
    )
):
    """
    Initialize autodoc configuration and state.
    
    Creates the .autodoc/ directory with:
    - config.yaml: Configuration file with default settings
    - state.json: Initial state tracking file
    
    Use --force to reinitialize an existing setup (preserves existing state).
    """
    autodoc_path = get_state_path().parent
    config_path = autodoc_path / "config.yaml"

    # Check if already initialized
    if autodoc_path.exists() and not force:
        typer.echo(f"✗ AutoDoc is already initialized in {autodoc_path}")
        typer.echo("  Use --force to reinitialize")
        raise typer.Exit(code=1)
    
    # Create .autodoc directory
    autodoc_path.mkdir(exist_ok=True)
    
    # Generate and save default configuration
    config = AutodocConfig.default()
    config.save(config_path)
    
    # Create or update state file
    if force and get_state_path().exists():
        # Preserve existing state when reinitializing
        typer.echo(f"✓ Reinitialized configuration (preserved existing state)")
    else:
        # Use state module to create properly structured initial state
        state = default_state()
        state["repo"]["root"] = str(Path.cwd())
        save_state(state)
        typer.echo(f"✓ Initialized AutoDoc in {autodoc_path}")
    
    # Show next steps
    typer.echo("\nNext steps:")
    typer.echo("  1. Review and customize .autodoc/config.yaml")
    typer.echo("  2. Run 'autodoc scan' to analyze your repository")
    typer.echo("  3. Run 'autodoc generate' to create documentation")
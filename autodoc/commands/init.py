import typer
from pathlib import Path

from autodoc.core.state import default_state, save_state, get_state_path

app = typer.Typer(
    help="Initialize AutoDoc configuration in the repository"
)


@app.callback(invoke_without_command=True)
def init(ctx: typer.Context):
    """
    Initialize autodoc configuration and state.
    """
    autodoc_path = get_state_path().parent

    if autodoc_path.exists():
        typer.echo(f"AutoDoc is already initialized in {autodoc_path}")
        raise typer.Exit(code=1)
    
    autodoc_path.mkdir()
    (autodoc_path / "config.yaml").write_text("# autodoc config\n")
    
    # Use state module to create properly structured initial state
    state = default_state()
    state["repo"]["root"] = str(Path.cwd())
    save_state(state)

    typer.echo("Initialized AutoDoc configuration in this repository")
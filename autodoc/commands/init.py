import typer
from pathlib import Path

app = typer.Typer(
    help="Initialize AutoDoc configuration in the repository"
)

AUTODOC_DIR = ".autodoc"

@app.command()
def init():
    """
    Initialize autodoc configuration and state.
    """
    root = Path.cwd()
    autodoc_path = root / AUTODOC_DIR

    if autodoc_path.exists():
        typer.echo(f"AutoDoc is already initialized in {autodoc_path}")
        raise typer.Exit(code=1)
    
    autodoc_path.mkdir()
    (autodoc_path / "config.yaml").write_text("# autodoc config\n")
    (autodoc_path / "state.json").write_text("{}\n")

    typer.echo(f"Initialized AutoDoc configuration in this repository")
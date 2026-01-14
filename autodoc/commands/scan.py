import typer

from autodoc.core.state import get_state_path

app = typer.Typer(
    help="Scan Repository and update the structural state accordingly"
)


@app.command()
def scan():
    """
    Scan repository and update the structural state accordingly.
    """
    autodoc_dir = get_state_path().parent

    if not autodoc_dir.exists():
        typer.echo("AutoDoc is not initialized in this repository. Please run 'autodoc init' first.")
        raise typer.Exit(code=1)
    
    typer.echo("Scanning the repository...")

    # TODO: Call Workflow A here

    typer.echo("Scan completed and state updated.")
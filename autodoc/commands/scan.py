import typer

from autodoc.core.repository import Repository
from autodoc.core.scan import get_changed_files, scan_repository, summarize_changes
from autodoc.core.state import get_state_path, load_state, save_state

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

    # Load current state
    state = load_state()
    
    # Get repository context
    repo = Repository.from_cwd()
    
    # Scan repository and detect changes
    changes = scan_repository(repo, state)
    
    # Save updated state
    save_state(state)
    
    # Display results
    summary = summarize_changes(changes)
    typer.echo(f"\nScan completed!")
    typer.echo(f"  Total files: {summary['total']}")
    typer.echo(f"  New: {summary['new']}")
    typer.echo(f"  Modified: {summary['modified']}")
    typer.echo(f"  Deleted: {summary['deleted']}")
    typer.echo(f"  Unchanged: {summary['unchanged']}")
    
    # Show changed files if any
    changed = get_changed_files(changes)
    if changed:
        typer.echo(f"\nChanged files ({len(changed)}):")
        for change in changed:
            typer.echo(f"  [{change.change_type.value.upper()}] {change.path}")
    else:
        typer.echo("\nNo changes detected.")
import typer

from autodoc.core.repository import Repository
from autodoc.core.scan import scan_repository, apply_scan_to_state
from autodoc.core.state import get_state_path, load_state, save_state

app = typer.Typer(
    help="Scan Repository and update the structural state accordingly"
)


@app.callback(invoke_without_command=True)
def scan(ctx: typer.Context):
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
    try:
        repo = Repository.from_cwd()
    except ValueError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)
    
    # Scan repository and detect changes
    scan_result = scan_repository(repo, state)
    
    # Apply scan results to state
    apply_scan_to_state(state, scan_result, repo)
    
    # Save updated state
    save_state(state)
    
    # Display results
    typer.echo(f"\nScan completed!")
    typer.echo(f"  Total files: {scan_result.total_files}")
    typer.echo(f"  Added: {len(scan_result.added)}")
    typer.echo(f"  Modified: {len(scan_result.modified)}")
    typer.echo(f"  Deleted: {len(scan_result.deleted)}")
    typer.echo(f"  Unchanged: {len(scan_result.unchanged)}")
    
    # Show changed files if any
    if scan_result.has_changes:
        typer.echo(f"\nChanged files:")
        for path in scan_result.added:
            typer.echo(f"  [ADDED] {path}")
        for path in scan_result.modified:
            typer.echo(f"  [MODIFIED] {path}")
        for path in scan_result.deleted:
            typer.echo(f"  [DELETED] {path}")
    else:
        typer.echo("\nNo changes detected.")

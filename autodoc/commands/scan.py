import typer

from autodoc.core.repository import Repository
from autodoc.core.scan import scan_repository, apply_scan_to_state
from autodoc.core.state import get_state_path, load_state, save_state
from autodoc.core.config import AutodocConfig
from autodoc.core.exceptions import NotInitializedError, RepositoryNotFoundError

app = typer.Typer(
    help="Scan Repository and update the structural state accordingly"
)


@app.callback(invoke_without_command=True)
def scan(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed scanning output"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview changes without saving state"),
):
    """
    Scan repository and update the structural state accordingly.
    """
    autodoc_dir = get_state_path().parent

    if not autodoc_dir.exists():
        raise NotInitializedError()
    
    # Load configuration
    try:
        config = AutodocConfig.from_autodoc_dir(autodoc_dir)
        # Override config with CLI flags if provided
        config.verbose = verbose or config.verbose
        config.dry_run = dry_run or config.dry_run
    except Exception as e:
        typer.echo(f"Warning: Could not load config, using defaults: {e}")
        config = AutodocConfig.default()
        config.verbose = verbose
        config.dry_run = dry_run
    
    if config.verbose:
        typer.echo(f"Configuration loaded from {autodoc_dir / 'config.yaml'}")
        typer.echo(f"Exclude patterns: {len(config.exclude_patterns)} patterns")
    
    typer.echo("Scanning the repository...")

    # Load current state
    state = load_state()
    
    # Get repository context
    try:
        repo = Repository.from_cwd()
        if config.verbose:
            typer.echo(f"Repository: {repo.name}")
            typer.echo(f"Root: {repo.root}")
            typer.echo(f"Branch: {repo.branch}")
    except ValueError as e:
        raise RepositoryNotFoundError(str(e))
    
    # Scan repository and detect changes
    if config.verbose:
        typer.echo(f"\nScanning files...")
    
    scan_result = scan_repository(repo, state)
    
    if config.verbose and scan_result.added:
        typer.echo(f"Found {len(scan_result.added)} new files:")
        for path in list(scan_result.added)[:5]:  # Show first 5
            typer.echo(f"  + {path}")
        if len(scan_result.added) > 5:
            typer.echo(f"  ... and {len(scan_result.added) - 5} more")
    
    # Apply scan results to state
    apply_scan_to_state(state, scan_result, repo)
    
    # Save updated state (unless dry-run)
    if not config.dry_run:
        save_state(state)
        if config.verbose:
            typer.echo(f"\n✓ State saved to {get_state_path()}")
    else:
        typer.echo(f"\n[DRY RUN] Would save state to {get_state_path()}")
    
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

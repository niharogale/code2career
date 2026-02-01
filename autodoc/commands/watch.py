import typer
import time
from pathlib import Path
from typing import Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from autodoc.core.repository import Repository
from autodoc.core.scan import scan_repository, apply_scan_to_state
from autodoc.core.state import get_state_path, load_state, save_state
from autodoc.core.config import AutodocConfig
from autodoc.core.exceptions import NotInitializedError, RepositoryNotFoundError
from autodoc.generation.readme_generator import generate_readme, write_readme

app = typer.Typer(
    help="Watch repository for changes and automatically update documentation"
)


class AutodocFileSystemEventHandler(FileSystemEventHandler):
    """
    File system event handler for autodoc watch mode.
    
    Monitors file system changes and triggers scans and README regeneration
    when relevant files are modified.
    """
    
    def __init__(
        self,
        repo: Repository,
        config: AutodocConfig,
        debounce_seconds: float = 2.0,
        auto_readme: bool = True,
    ):
        """
        Initialize the event handler.
        
        Args:
            repo: Repository instance
            config: AutodocConfig instance
            debounce_seconds: Time to wait before processing changes (debouncing)
            auto_readme: Whether to automatically regenerate README on changes
        """
        super().__init__()
        self.repo = repo
        self.config = config
        self.debounce_seconds = debounce_seconds
        self.auto_readme = auto_readme
        self.pending_changes: Set[str] = set()
        self.last_change_time: Optional[float] = None
        self.processing = False
    
    def should_process_path(self, path: str) -> bool:
        """
        Check if a path should trigger a scan.
        
        Args:
            path: File path to check
            
        Returns:
            True if the path should be processed, False otherwise
        """
        path_obj = Path(path)
        
        # Ignore .autodoc directory
        if ".autodoc" in path_obj.parts:
            return False
        
        # Ignore .git directory
        if ".git" in path_obj.parts:
            return False
        
        # Check against exclude patterns
        for pattern in self.config.exclude_patterns:
            if path_obj.match(pattern):
                return False
        
        # Check against include patterns
        for pattern in self.config.include_patterns:
            if path_obj.match(pattern):
                return True
        
        return False
    
    def on_any_event(self, event: FileSystemEvent):
        """
        Handle any file system event.
        
        Args:
            event: File system event
        """
        # Ignore directory events
        if event.is_directory:
            return
        
        # Check if we should process this path
        if not self.should_process_path(event.src_path):
            return
        
        # Add to pending changes
        self.pending_changes.add(event.src_path)
        self.last_change_time = time.time()
        
        if self.config.verbose:
            event_type = event.event_type
            typer.echo(f"[{event_type}] {event.src_path}")
    
    def process_pending_changes(self) -> bool:
        """
        Process pending changes if debounce period has elapsed.
        
        Returns:
            True if changes were processed, False otherwise
        """
        if not self.pending_changes:
            return False
        
        if self.last_change_time is None:
            return False
        
        # Check if debounce period has elapsed
        elapsed = time.time() - self.last_change_time
        if elapsed < self.debounce_seconds:
            return False
        
        # Prevent concurrent processing
        if self.processing:
            return False
        
        self.processing = True
        
        try:
            typer.echo(f"\n📝 Processing {len(self.pending_changes)} file change(s)...")
            
            # Load current state
            state = load_state()
            
            # Scan repository
            scan_result = scan_repository(self.repo, state)
            
            # Apply scan results to state
            apply_scan_to_state(state, scan_result, self.repo, scan_result.dependency_graph)
            
            # Save updated state
            save_state(state)
            
            # Display results
            if scan_result.has_changes:
                typer.echo(f"✓ Scan completed: {len(scan_result.added)} added, "
                          f"{len(scan_result.modified)} modified, "
                          f"{len(scan_result.deleted)} deleted")
                
                # Auto-regenerate README if enabled
                if self.auto_readme:
                    typer.echo("📄 Regenerating README...")
                    readme_content = generate_readme(state)
                    write_readme(self.repo.root, readme_content)
                    typer.echo("✓ README updated")
            else:
                typer.echo("✓ No significant changes detected")
            
            # Clear pending changes
            self.pending_changes.clear()
            self.last_change_time = None
            
            typer.echo("👀 Watching for changes...\n")
            
            return True
            
        except Exception as e:
            typer.echo(f"❌ Error processing changes: {e}", err=True)
            if self.config.verbose:
                import traceback
                typer.echo(traceback.format_exc(), err=True)
            return False
        finally:
            self.processing = False


@app.callback(invoke_without_command=True)
def watch(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    debounce: float = typer.Option(2.0, "--debounce", "-d", help="Seconds to wait before processing changes"),
    no_readme: bool = typer.Option(False, "--no-readme", help="Don't automatically regenerate README"),
    interval: float = typer.Option(1.0, "--interval", "-i", help="Polling interval in seconds"),
):
    """
    Watch repository for changes and automatically update documentation.
    
    This command monitors the repository for file changes and automatically:
    1. Scans changed files
    2. Updates the state
    3. Regenerates the README (unless --no-readme is specified)
    
    The watch mode uses debouncing to avoid processing changes too frequently.
    Changes are batched and processed after the debounce period elapses.
    """
    autodoc_dir = get_state_path().parent

    if not autodoc_dir.exists():
        raise NotInitializedError()
    
    # Load configuration
    try:
        config = AutodocConfig.from_autodoc_dir(autodoc_dir)
        config.verbose = verbose or config.verbose
    except Exception as e:
        typer.echo(f"Warning: Could not load config, using defaults: {e}")
        config = AutodocConfig.default()
        config.verbose = verbose
    
    # Get repository context
    try:
        repo = Repository.from_cwd()
        if config.verbose:
            typer.echo(f"Repository: {repo.name}")
            typer.echo(f"Root: {repo.root}")
            typer.echo(f"Branch: {repo.branch}")
    except ValueError as e:
        raise RepositoryNotFoundError(str(e))
    
    # Create event handler
    event_handler = AutodocFileSystemEventHandler(
        repo=repo,
        config=config,
        debounce_seconds=debounce,
        auto_readme=not no_readme,
    )
    
    # Create and start observer
    observer = Observer()
    observer.schedule(event_handler, str(repo.root), recursive=True)
    observer.start()
    
    typer.echo(f"👀 Watching {repo.root} for changes...")
    typer.echo(f"   Debounce: {debounce}s | Auto-README: {not no_readme}")
    typer.echo("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(interval)
            # Process pending changes if debounce period has elapsed
            event_handler.process_pending_changes()
    except KeyboardInterrupt:
        typer.echo("\n\n👋 Stopping watch mode...")
        observer.stop()
    
    observer.join()
    typer.echo("✓ Watch mode stopped")

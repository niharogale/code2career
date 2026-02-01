import typer
from autodoc.commands import init, scan, generate, watch

app = typer.Typer(
    help="AutoDoc: Automatically generate documentation from your codebase"
)

app.add_typer(init.app, name="init", help="Initialize AutoDoc configuration in the repository")
app.add_typer(scan.app, name="scan", help="Scan the codebase to analyze structure and components")
app.add_typer(generate.app, name="generate", help="Generate README and resume based on the scan results")
app.add_typer(watch.app, name="watch", help="Watch repository for changes and automatically update documentation")

if __name__ == "__main__":
    app()
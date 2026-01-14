import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

STATE_PATH = Path.cwd() / ".autodoc" / "state.json"


def default_state() -> Dict[str, Any]:
    """
    Returns a default state according to the state schema
    """
    return {
        "version": "1.0",
        "repo": {
            "name": "",
            "root": "",
            "branch": "",
            "commit": ""
        },
        "last_scan": "",
        "files": {},
        "readme_sections": {}
    }


def get_state_path() -> Path:
    """
    Returns the path to the state file.
    Centralizes state file location for consistency across the codebase.
    """
    return STATE_PATH


def load_state() -> Dict[str, Any]:
    """
    Load the state from the .autodoc/state.json
    If the file doesn't exist or is empty/invalid, return a default state
    """
    if not STATE_PATH.exists():
        return default_state()
    
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
            # Handle empty state file or missing required keys
            if not state or "version" not in state:
                return default_state()
            return state
    except (json.JSONDecodeError, IOError):
        return default_state()
    
def save_state(state: Dict[str, Any]) -> None:
    """
    Save the state to the .autodoc/state.json
    """
    STATE_PATH.parent.mkdir(exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def update_file(
    state: Dict[str, Any],
    file_path: str,
    file_hash: str,
    change_type: str,
    last_modified: Optional[str] = None
):
    """
    Update or add a file entry in state['files'].
    """
    if last_modified is None:
        last_modified = datetime.now(timezone.utc).isoformat()
    
    state["files"][file_path] = {
        "hash": file_hash,
        "change_type": change_type,
        "last_modified": last_modified
    }


def remove_file(state: Dict[str, Any], file_path: str):
    """
    Remove a file entry from the state.
    """
    if file_path in state["files"]:
        del state["files"][file_path]

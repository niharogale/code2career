import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from autodoc.core.exceptions import StateCorruptedError

STATE_PATH = Path.cwd() / ".autodoc" / "state.json"
logger = logging.getLogger(__name__)


def default_state() -> Dict[str, Any]:
    """
    Returns a default state according to the state schema
    """
    return {
        "version": "1.1",
        "repo": {
            "name": "",
            "root": "",
            "branch": "",
            "commit": ""
        },
        "last_scan": "",
        "files": {},
        "readme_sections": {},
        "dependency_graph": {}
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
            
            # Handle empty state file
            if not state:
                logger.warning("State file is empty, returning default state")
                return default_state()
            
            # Validate state structure
            if not isinstance(state, dict):
                logger.warning(f"State file contains invalid type {type(state)}, returning default state")
                return default_state()
            
            # Check for required keys
            if "version" not in state:
                logger.warning("State file missing 'version' key, returning default state")
                return default_state()
            
            # Validate required structure
            required_keys = ["version", "repo", "files"]
            missing_keys = [key for key in required_keys if key not in state]
            if missing_keys:
                logger.warning(f"State file missing required keys: {missing_keys}, returning default state")
                return default_state()
            
            # Handle migration from v1.0 to v1.1
            if state.get("version") == "1.0":
                logger.info("Migrating state from v1.0 to v1.1")
                state["version"] = "1.1"
                if "dependency_graph" not in state:
                    state["dependency_graph"] = {}
            
            return state
            
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse state file as JSON: {e}, returning default state")
        return default_state()
    except IOError as e:
        logger.warning(f"Failed to read state file: {e}, returning default state")
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
    last_modified: Optional[str] = None,
    ast_hash: Optional[str] = None,
    semantic_category: Optional[str] = None,
    definitions: Optional[list] = None,
    imports: Optional[list] = None,
    language: Optional[str] = None
):
    """
    Update or add a file entry in state['files'].
    """
    if last_modified is None:
        last_modified = datetime.now(timezone.utc).isoformat()
    
    file_entry = {
        "hash": file_hash,
        "change_type": change_type,
        "last_modified": last_modified
    }
    
    # Add optional AST metadata
    if language:
        file_entry["language"] = language
    if ast_hash:
        file_entry["ast_hash"] = ast_hash
    if semantic_category:
        file_entry["semantic_category"] = semantic_category
    if definitions:
        file_entry["definitions"] = definitions
    if imports:
        file_entry["imports"] = imports
    
    state["files"][file_path] = file_entry


def remove_file(state: Dict[str, Any], file_path: str):
    """
    Remove a file entry from the state.
    """
    if file_path in state["files"]:
        del state["files"][file_path]

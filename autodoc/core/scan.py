# autodoc/core/scan.py
"""
Repository scanning module - enumerates files and computes hashes.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib
import logging

from autodoc.core.repository import Repository
from autodoc.analysis.ast_parser import ASTParser, TREE_SITTER_AVAILABLE
from autodoc.analysis.dependency_graph import DependencyGraph
from autodoc.analysis.semantic_changes import SemanticChangeAnalyzer

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes detected between scans."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


@dataclass
class FileChange:
    """Represents a change to a single file."""
    path: str
    change_type: ChangeType
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    old_ast_hash: Optional[str] = None
    new_ast_hash: Optional[str] = None
    semantic_category: Optional[str] = None
    language: Optional[str] = None
    definitions: List[Dict] = None
    imports: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize mutable default values."""
        if self.definitions is None:
            self.definitions = []
        if self.imports is None:
            self.imports = []

    def to_dict(self) -> dict:
        """Convert to dictionary for state storage."""
        result = {
            "hash": self.new_hash or self.old_hash or "",
            "change_type": self.change_type.value,
            "language": self.language,
            "last_modified": datetime.now(timezone.utc).isoformat()
        }
        
        # Add AST metadata if available
        if self.new_ast_hash or self.old_ast_hash:
            result["ast_hash"] = self.new_ast_hash or self.old_ast_hash
        
        if self.semantic_category:
            result["semantic_category"] = self.semantic_category
        
        if self.definitions:
            result["definitions"] = self.definitions
        
        if self.imports:
            result["imports"] = self.imports
        
        return result


@dataclass
class ScanResult:
    """Result of a repository scan."""
    files: Dict[str, FileChange]
    added: List[str]
    modified: List[str]
    deleted: List[str]
    unchanged: List[str]
    dependency_graph: Optional[DependencyGraph] = None
    
    @property
    def has_changes(self) -> bool:
        """Check if any changes were detected."""
        return bool(self.added or self.modified or self.deleted)
    
    @property
    def total_files(self) -> int:
        """Total number of tracked files."""
        return len(self.files)
    
    def summary(self) -> str:
        """Human-readable summary of scan results."""
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.modified:
            parts.append(f"{len(self.modified)} modified")
        if self.deleted:
            parts.append(f"{len(self.deleted)} deleted")
        if self.unchanged:
            parts.append(f"{len(self.unchanged)} unchanged")
        
        if not parts:
            return "No files found"
        return ", ".join(parts)


def compute_file_hash(path: Path) -> str:
    """
    Compute a stable SHA-256 hash for a file's contents.
    
    Args:
        path: Path to the file to hash
        
    Returns:
        Hex string of the SHA-256 hash
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_file_ast(
    file_path: Path, 
    language: Optional[str],
    ast_enabled: bool = True
) -> tuple[Optional[str], List[Dict], List[str]]:
    """
    Parse a file's AST and extract metadata.
    
    Args:
        file_path: Path to the file
        language: Programming language of the file
        ast_enabled: Whether AST parsing is enabled
        
    Returns:
        Tuple of (ast_hash, definitions_list, imports_list)
    """
    # Skip if AST parsing is disabled or tree-sitter not available
    if not ast_enabled or not TREE_SITTER_AVAILABLE:
        return None, [], []
    
    # Skip if language is not supported
    if not language or not ASTParser.is_supported_language(language):
        return None, [], []
    
    try:
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        
        # Initialize parser for this language
        parser = ASTParser(language)
        
        # Parse the AST
        ast = parser.parse(source_code)
        
        if not ast.is_valid():
            logger.debug(f"Failed to parse AST for {file_path}")
            return None, [], []
        
        # Compute AST hash
        ast_hash = parser.compute_ast_hash(ast)
        
        # Extract definitions
        definitions = parser.extract_definitions(ast)
        definitions_list = [
            {
                "name": d.name,
                "type": d.type.value,
                "line": d.line,
                "is_public": d.is_public
            }
            for d in definitions
        ]
        
        # Extract imports
        imports = parser.extract_imports(ast)
        imports_list = list(imports)
        
        return ast_hash, definitions_list, imports_list
        
    except Exception as e:
        logger.warning(f"Error parsing AST for {file_path}: {e}")
        return None, [], []


def scan_repository(
    repo: Repository, 
    previous_state: Dict[str, Any],
    ast_enabled: bool = True,
    semantic_analysis_enabled: bool = True
) -> ScanResult:
    """
    Scan a repository and detect changes since the last scan.
    
    Args:
        repo: Repository context
        previous_state: State dict from the previous scan (with 'files' key)
        ast_enabled: Whether to enable AST parsing (default: True)
        semantic_analysis_enabled: Whether to enable semantic analysis (default: True)
        
    Returns:
        ScanResult containing all file changes
    """
    previous_files = previous_state.get("files", {})
    current_files: Dict[str, FileChange] = {}
    
    added: List[str] = []
    modified: List[str] = []
    deleted: List[str] = []
    unchanged: List[str] = []
    
    # Initialize dependency graph
    dependency_graph = DependencyGraph()
    
    # Initialize semantic analyzer if enabled
    semantic_analyzer = SemanticChangeAnalyzer() if semantic_analysis_enabled else None
    
    # Get all source files from the repository
    source_files = repo.get_source_files()
    current_paths = set()
    
    # Process each current file
    for file_path in source_files:
        rel_path = repo.get_relative_path(file_path)
        current_paths.add(rel_path)
        
        try:
            new_hash = compute_file_hash(file_path)
        except (IOError, OSError):
            # Skip files we can't read
            continue
        
        language = repo.get_language(file_path)
        old_info = previous_files.get(rel_path)
        
        # Parse AST and extract metadata
        ast_hash, definitions, imports = parse_file_ast(file_path, language, ast_enabled)
        
        # Add to dependency graph
        if imports:
            dependency_graph.add_file(rel_path, set(imports), language)
        
        # Determine change type and create FileChange
        if old_info is None:
            # New file
            change = FileChange(
                path=rel_path,
                change_type=ChangeType.ADDED,
                new_hash=new_hash,
                new_ast_hash=ast_hash,
                language=language,
                definitions=definitions,
                imports=imports
            )
            added.append(rel_path)
            
            # Semantic analysis for new file
            if semantic_analyzer and ast_hash:
                from autodoc.analysis.ast_parser import Definition, DefinitionType
                defs = [
                    Definition(
                        name=d["name"],
                        type=DefinitionType(d["type"]),
                        line=d["line"],
                        is_public=d["is_public"]
                    )
                    for d in definitions
                ]
                
                # For new files, old version doesn't exist
                semantic_result = semantic_analyzer.classify_change(
                    old_definitions=[],
                    new_definitions=defs,
                    old_hash=None,
                    new_hash=new_hash,
                    old_ast_hash=None,
                    new_ast_hash=ast_hash,
                    file_exists_old=False,
                    file_exists_new=True
                )
                change.semantic_category = semantic_result.category.value
        
        elif old_info.get("hash") != new_hash:
            # Modified file
            old_hash = old_info.get("hash")
            old_ast_hash = old_info.get("ast_hash")
            old_definitions = old_info.get("definitions", [])
            
            change = FileChange(
                path=rel_path,
                change_type=ChangeType.MODIFIED,
                old_hash=old_hash,
                new_hash=new_hash,
                old_ast_hash=old_ast_hash,
                new_ast_hash=ast_hash,
                language=language,
                definitions=definitions,
                imports=imports
            )
            modified.append(rel_path)
            
            # Semantic analysis for modified file
            if semantic_analyzer and ast_hash:
                from autodoc.analysis.ast_parser import Definition, DefinitionType
                
                old_defs = [
                    Definition(
                        name=d["name"],
                        type=DefinitionType(d["type"]),
                        line=d["line"],
                        is_public=d["is_public"]
                    )
                    for d in old_definitions
                ]
                
                new_defs = [
                    Definition(
                        name=d["name"],
                        type=DefinitionType(d["type"]),
                        line=d["line"],
                        is_public=d["is_public"]
                    )
                    for d in definitions
                ]
                
                semantic_result = semantic_analyzer.classify_change(
                    old_definitions=old_defs,
                    new_definitions=new_defs,
                    old_hash=old_hash,
                    new_hash=new_hash,
                    old_ast_hash=old_ast_hash,
                    new_ast_hash=ast_hash,
                    file_exists_old=True,
                    file_exists_new=True
                )
                change.semantic_category = semantic_result.category.value
        
        else:
            # Unchanged file - preserve existing AST metadata if available
            change = FileChange(
                path=rel_path,
                change_type=ChangeType.UNCHANGED,
                old_hash=old_info.get("hash"),
                new_hash=new_hash,
                old_ast_hash=old_info.get("ast_hash"),
                new_ast_hash=old_info.get("ast_hash"),  # Use old hash since unchanged
                language=language,
                definitions=old_info.get("definitions", []),
                imports=old_info.get("imports", [])
            )
            unchanged.append(rel_path)
            
            # If we don't have AST metadata yet, parse it now
            if ast_hash and not old_info.get("ast_hash"):
                change.new_ast_hash = ast_hash
                change.definitions = definitions
                change.imports = imports
        
        current_files[rel_path] = change
    
    # Detect deleted files
    for old_path in previous_files:
        if old_path not in current_paths:
            old_info = previous_files[old_path]
            old_definitions = old_info.get("definitions", [])
            
            change = FileChange(
                path=old_path,
                change_type=ChangeType.DELETED,
                old_hash=old_info.get("hash"),
                old_ast_hash=old_info.get("ast_hash"),
                language=old_info.get("language"),
                definitions=old_definitions,
                imports=old_info.get("imports", [])
            )
            deleted.append(old_path)
            
            # Semantic analysis for deleted file
            if semantic_analyzer and old_definitions:
                from autodoc.analysis.ast_parser import Definition, DefinitionType
                
                old_defs = [
                    Definition(
                        name=d["name"],
                        type=DefinitionType(d["type"]),
                        line=d["line"],
                        is_public=d["is_public"]
                    )
                    for d in old_definitions
                ]
                
                semantic_result = semantic_analyzer.classify_change(
                    old_definitions=old_defs,
                    new_definitions=[],
                    old_hash=old_info.get("hash"),
                    new_hash=None,
                    old_ast_hash=old_info.get("ast_hash"),
                    new_ast_hash=None,
                    file_exists_old=True,
                    file_exists_new=False
                )
                change.semantic_category = semantic_result.category.value
            
            current_files[old_path] = change
    
    return ScanResult(
        files=current_files,
        added=added,
        modified=modified,
        deleted=deleted,
        unchanged=unchanged,
        dependency_graph=dependency_graph if ast_enabled else None
    )


def apply_scan_to_state(
    state: Dict[str, Any], 
    scan_result: ScanResult, 
    repo: Repository,
    dependency_graph: Optional[DependencyGraph] = None
) -> None:
    """
    Apply scan results to the state dictionary.
    
    Args:
        state: State dictionary to update (modified in place)
        scan_result: Results from scan_repository()
        repo: Repository context
        dependency_graph: Optional dependency graph to save
    """
    # Update repo metadata
    state["repo"] = repo.to_dict()
    state["last_scan"] = datetime.now(timezone.utc).isoformat()
    
    # Update files - remove deleted, update/add others
    new_files = {}
    for path, change in scan_result.files.items():
        if change.change_type != ChangeType.DELETED:
            new_files[path] = change.to_dict()
    
    state["files"] = new_files
    
    # Save dependency graph if provided
    if dependency_graph:
        state["dependency_graph"] = dependency_graph.to_dict()
    
    # Ensure version is updated
    if state.get("version") == "1.0":
        state["version"] = "1.1"

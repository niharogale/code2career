"""Semantic change detection for classifying code modifications."""

import logging
from typing import List, Set, Dict, Optional
from enum import Enum
from dataclasses import dataclass

from autodoc.analysis.ast_parser import Definition, DefinitionType, ParsedAST

logger = logging.getLogger(__name__)


class ChangeCategory(str, Enum):
    """Categories of semantic changes."""
    BREAKING = "breaking"          # Removed public API, changed signatures
    ADDITIVE = "additive"          # Added new APIs, optional parameters
    INTERNAL = "internal"          # Changes to private/internal code only
    DOCS_ONLY = "docs-only"        # Only comments/docstrings changed
    UNKNOWN = "unknown"            # Unable to classify


@dataclass
class DefinitionChange:
    """Represents a change to a specific definition (function, class, etc.)."""
    name: str
    definition_type: DefinitionType
    change_type: str  # "added", "removed", "modified", "unchanged"
    old_line: Optional[int] = None
    new_line: Optional[int] = None
    is_public: bool = True


@dataclass
class SemanticChangeResult:
    """Result of semantic change analysis."""
    category: ChangeCategory
    definition_changes: List[DefinitionChange]
    has_breaking_changes: bool
    has_additions: bool
    has_removals: bool
    description: str


class SemanticChangeAnalyzer:
    """
    Analyzes changes between versions of a file to classify them semantically.
    
    This analyzer compares AST structures to determine the nature and impact
    of changes, going beyond simple file hash comparison.
    """
    
    def __init__(self):
        """Initialize the semantic change analyzer."""
        pass
    
    def classify_change(
        self,
        old_ast: Optional[ParsedAST],
        new_ast: Optional[ParsedAST],
        old_definitions: List[Definition],
        new_definitions: List[Definition],
        old_hash: Optional[str] = None,
        new_hash: Optional[str] = None,
        old_ast_hash: Optional[str] = None,
        new_ast_hash: Optional[str] = None,
    ) -> SemanticChangeResult:
        """
        Classify the semantic nature of changes between two versions of a file.
        
        Args:
            old_ast: Parsed AST of the old version (None if file is new)
            new_ast: Parsed AST of the new version (None if file is deleted)
            old_definitions: List of definitions from the old version
            new_definitions: List of definitions from the new version
            old_hash: File content hash of old version
            new_hash: File content hash of new version
            old_ast_hash: AST structure hash of old version
            new_ast_hash: AST structure hash of new version
            
        Returns:
            SemanticChangeResult with classification and details
        """
        # Handle file creation
        if old_ast is None and new_ast is not None:
            return self._classify_file_creation(new_definitions)
        
        # Handle file deletion
        if new_ast is None and old_ast is not None:
            return self._classify_file_deletion(old_definitions)
        
        # Both exist - analyze changes
        if old_ast is not None and new_ast is not None:
            return self._classify_file_modification(
                old_definitions,
                new_definitions,
                old_hash,
                new_hash,
                old_ast_hash,
                new_ast_hash,
            )
        
        # Edge case: both None
        return SemanticChangeResult(
            category=ChangeCategory.UNKNOWN,
            definition_changes=[],
            has_breaking_changes=False,
            has_additions=False,
            has_removals=False,
            description="Unable to classify change (both versions missing)",
        )
    
    def _classify_file_creation(self, definitions: List[Definition]) -> SemanticChangeResult:
        """Classify a newly created file."""
        public_defs = [d for d in definitions if d.is_public]
        
        def_changes = [
            DefinitionChange(
                name=d.name,
                definition_type=d.type,
                change_type="added",
                new_line=d.line,
                is_public=d.is_public,
            )
            for d in definitions
        ]
        
        description = f"New file with {len(definitions)} definition(s)"
        if public_defs:
            description += f" ({len(public_defs)} public)"
        
        return SemanticChangeResult(
            category=ChangeCategory.ADDITIVE,
            definition_changes=def_changes,
            has_breaking_changes=False,
            has_additions=True,
            has_removals=False,
            description=description,
        )
    
    def _classify_file_deletion(self, definitions: List[Definition]) -> SemanticChangeResult:
        """Classify a deleted file."""
        public_defs = [d for d in definitions if d.is_public]
        
        def_changes = [
            DefinitionChange(
                name=d.name,
                definition_type=d.type,
                change_type="removed",
                old_line=d.line,
                is_public=d.is_public,
            )
            for d in definitions
        ]
        
        has_breaking = len(public_defs) > 0
        
        description = f"File deleted with {len(definitions)} definition(s)"
        if public_defs:
            description += f" ({len(public_defs)} public - BREAKING)"
        
        return SemanticChangeResult(
            category=ChangeCategory.BREAKING if has_breaking else ChangeCategory.INTERNAL,
            definition_changes=def_changes,
            has_breaking_changes=has_breaking,
            has_additions=False,
            has_removals=True,
            description=description,
        )
    
    def _classify_file_modification(
        self,
        old_definitions: List[Definition],
        new_definitions: List[Definition],
        old_hash: Optional[str],
        new_hash: Optional[str],
        old_ast_hash: Optional[str],
        new_ast_hash: Optional[str],
    ) -> SemanticChangeResult:
        """Classify modifications to an existing file."""
        # Check if AST hash is unchanged (docs-only changes)
        if old_ast_hash and new_ast_hash and old_ast_hash == new_ast_hash:
            # File content changed but AST structure is the same
            # This means only comments, whitespace, or docstrings changed
            return SemanticChangeResult(
                category=ChangeCategory.DOCS_ONLY,
                definition_changes=[],
                has_breaking_changes=False,
                has_additions=False,
                has_removals=False,
                description="Documentation-only changes (comments, docstrings, whitespace)",
            )
        
        # Build maps of definitions by name for comparison
        old_def_map = {d.name: d for d in old_definitions}
        new_def_map = {d.name: d for d in new_definitions}
        
        # Analyze definition changes
        def_changes = []
        added_public = []
        removed_public = []
        modified_public = []
        
        # Find removed definitions
        for name, old_def in old_def_map.items():
            if name not in new_def_map:
                def_changes.append(
                    DefinitionChange(
                        name=name,
                        definition_type=old_def.type,
                        change_type="removed",
                        old_line=old_def.line,
                        is_public=old_def.is_public,
                    )
                )
                if old_def.is_public:
                    removed_public.append(old_def)
        
        # Find added and modified definitions
        for name, new_def in new_def_map.items():
            if name not in old_def_map:
                # Added definition
                def_changes.append(
                    DefinitionChange(
                        name=name,
                        definition_type=new_def.type,
                        change_type="added",
                        new_line=new_def.line,
                        is_public=new_def.is_public,
                    )
                )
                if new_def.is_public:
                    added_public.append(new_def)
            else:
                # Potentially modified definition
                old_def = old_def_map[name]
                if self._is_definition_modified(old_def, new_def):
                    def_changes.append(
                        DefinitionChange(
                            name=name,
                            definition_type=new_def.type,
                            change_type="modified",
                            old_line=old_def.line,
                            new_line=new_def.line,
                            is_public=new_def.is_public,
                        )
                    )
                    if new_def.is_public:
                        modified_public.append(new_def)
        
        # Classify based on changes
        has_breaking = len(removed_public) > 0
        has_additions = len(added_public) > 0
        has_removals = len(removed_public) > 0
        
        # Determine category
        category = self._determine_change_category(
            added_public=added_public,
            removed_public=removed_public,
            modified_public=modified_public,
            all_changes=def_changes,
        )
        
        # Build description
        description = self._build_change_description(
            added_public=added_public,
            removed_public=removed_public,
            modified_public=modified_public,
            all_changes=def_changes,
        )
        
        return SemanticChangeResult(
            category=category,
            definition_changes=def_changes,
            has_breaking_changes=has_breaking,
            has_additions=has_additions,
            has_removals=has_removals,
            description=description,
        )
    
    def _is_definition_modified(self, old_def: Definition, new_def: Definition) -> bool:
        """
        Check if a definition has been modified.
        
        Currently checks if the type or public status changed.
        In the future, could check function signatures, etc.
        """
        return (
            old_def.type != new_def.type or
            old_def.is_public != new_def.is_public
        )
    
    def _determine_change_category(
        self,
        added_public: List[Definition],
        removed_public: List[Definition],
        modified_public: List[Definition],
        all_changes: List[DefinitionChange],
    ) -> ChangeCategory:
        """
        Determine the overall change category based on the changes.
        
        Priority order:
        1. BREAKING - if any public APIs were removed
        2. ADDITIVE - if only public APIs were added (no removals)
        3. INTERNAL - if only private/internal changes
        4. UNKNOWN - if unable to classify
        """
        # Any public removals = breaking
        if removed_public:
            return ChangeCategory.BREAKING
        
        # Only additions to public API = additive
        if added_public and not removed_public:
            return ChangeCategory.ADDITIVE
        
        # Check if all changes are to private/internal definitions
        public_changes = [
            c for c in all_changes
            if c.is_public and c.change_type != "unchanged"
        ]
        
        if not public_changes:
            # All changes are internal
            return ChangeCategory.INTERNAL
        
        # Public modifications without additions or removals
        if modified_public and not added_public and not removed_public:
            # Could be breaking, but we treat signature-preserving modifications as internal
            # In future, could analyze signatures more carefully
            return ChangeCategory.INTERNAL
        
        return ChangeCategory.UNKNOWN
    
    def _build_change_description(
        self,
        added_public: List[Definition],
        removed_public: List[Definition],
        modified_public: List[Definition],
        all_changes: List[DefinitionChange],
    ) -> str:
        """Build a human-readable description of the changes."""
        parts = []
        
        if removed_public:
            parts.append(f"Removed {len(removed_public)} public API(s)")
        
        if added_public:
            parts.append(f"Added {len(added_public)} public API(s)")
        
        if modified_public:
            parts.append(f"Modified {len(modified_public)} public API(s)")
        
        # Count internal changes
        internal_changes = [
            c for c in all_changes
            if not c.is_public and c.change_type != "unchanged"
        ]
        
        if internal_changes:
            parts.append(f"{len(internal_changes)} internal change(s)")
        
        if not parts:
            return "No significant changes detected"
        
        return "; ".join(parts)
    
    def analyze_import_impact(
        self,
        changed_file: str,
        change_result: SemanticChangeResult,
        dependents: Set[str],
    ) -> Dict[str, str]:
        """
        Analyze the potential impact of changes on dependent files.
        
        Args:
            changed_file: Path to the file that changed
            change_result: Semantic change analysis result
            dependents: Set of files that depend on the changed file
            
        Returns:
            Dictionary mapping dependent file paths to impact descriptions
        """
        impact = {}
        
        if not dependents:
            return impact
        
        if change_result.category == ChangeCategory.BREAKING:
            for dependent in dependents:
                impact[dependent] = (
                    f"May be broken by changes in {changed_file}: "
                    f"{change_result.description}"
                )
        
        elif change_result.category == ChangeCategory.ADDITIVE:
            for dependent in dependents:
                impact[dependent] = (
                    f"New APIs available from {changed_file}: "
                    f"{change_result.description}"
                )
        
        elif change_result.category == ChangeCategory.INTERNAL:
            for dependent in dependents:
                impact[dependent] = (
                    f"Internal changes in {changed_file} (no API impact expected)"
                )
        
        elif change_result.category == ChangeCategory.DOCS_ONLY:
            for dependent in dependents:
                impact[dependent] = (
                    f"Documentation updated in {changed_file} (no code impact)"
                )
        
        return impact
    
    def get_breaking_changes(
        self,
        change_result: SemanticChangeResult,
    ) -> List[DefinitionChange]:
        """
        Extract breaking changes from a semantic change result.
        
        Args:
            change_result: Semantic change analysis result
            
        Returns:
            List of definition changes that are breaking
        """
        breaking = []
        
        for change in change_result.definition_changes:
            # Public removals are breaking
            if change.is_public and change.change_type == "removed":
                breaking.append(change)
            
            # Type changes to public APIs are potentially breaking
            if change.is_public and change.change_type == "modified":
                breaking.append(change)
        
        return breaking
    
    def get_additive_changes(
        self,
        change_result: SemanticChangeResult,
    ) -> List[DefinitionChange]:
        """
        Extract additive changes from a semantic change result.
        
        Args:
            change_result: Semantic change analysis result
            
        Returns:
            List of definition changes that are additive
        """
        return [
            change
            for change in change_result.definition_changes
            if change.change_type == "added"
        ]
    
    def summarize_changes(
        self,
        changes: Dict[str, SemanticChangeResult],
    ) -> Dict[str, any]:
        """
        Summarize changes across multiple files.
        
        Args:
            changes: Dictionary mapping file paths to their semantic change results
            
        Returns:
            Summary dictionary with aggregated statistics
        """
        summary = {
            "total_files": len(changes),
            "by_category": {
                ChangeCategory.BREAKING: 0,
                ChangeCategory.ADDITIVE: 0,
                ChangeCategory.INTERNAL: 0,
                ChangeCategory.DOCS_ONLY: 0,
                ChangeCategory.UNKNOWN: 0,
            },
            "breaking_files": [],
            "additive_files": [],
            "total_additions": 0,
            "total_removals": 0,
            "total_modifications": 0,
        }
        
        for file_path, result in changes.items():
            # Count by category
            summary["by_category"][result.category] += 1
            
            # Track breaking and additive files
            if result.category == ChangeCategory.BREAKING:
                summary["breaking_files"].append(file_path)
            elif result.category == ChangeCategory.ADDITIVE:
                summary["additive_files"].append(file_path)
            
            # Count changes
            for change in result.definition_changes:
                if change.change_type == "added":
                    summary["total_additions"] += 1
                elif change.change_type == "removed":
                    summary["total_removals"] += 1
                elif change.change_type == "modified":
                    summary["total_modifications"] += 1
        
        return summary

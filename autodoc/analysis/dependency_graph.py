"""Dependency Graph for analyzing import relationships between files."""

import logging
from typing import Dict, Set, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict, deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DependencyNode:
    """Represents a file node in the dependency graph."""
    path: str
    imports: Set[str]
    language: Optional[str] = None


class DependencyGraph:
    """
    Manages dependency relationships between files in a codebase.
    
    This class builds and queries a directed graph where nodes are files
    and edges represent import/dependency relationships.
    """
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        # Map from file path to set of files it imports (dependencies)
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Map from file path to set of files that import it (dependents)
        self._dependents: Dict[str, Set[str]] = defaultdict(set)
        
        # Store metadata about each file
        self._nodes: Dict[str, DependencyNode] = {}
        
        # Cache for resolved import paths
        self._import_cache: Dict[Tuple[str, str], Optional[str]] = {}
    
    def add_file(self, path: str, imports: Set[str], language: Optional[str] = None) -> None:
        """
        Add a file to the dependency graph with its imports.
        
        Args:
            path: File path (relative to repository root)
            imports: Set of imported module/file names
            language: Programming language of the file
        """
        # Store the node
        self._nodes[path] = DependencyNode(
            path=path,
            imports=imports.copy(),
            language=language
        )
        
        # Clear old relationships for this file
        if path in self._dependencies:
            # Remove this file as a dependent from its old dependencies
            for old_dep in self._dependencies[path]:
                if old_dep in self._dependents:
                    self._dependents[old_dep].discard(path)
            self._dependencies[path].clear()
        
        # Resolve imports to actual file paths and build relationships
        for import_name in imports:
            resolved_path = self._resolve_import(path, import_name, language)
            
            if resolved_path:
                # Add dependency relationship
                self._dependencies[path].add(resolved_path)
                self._dependents[resolved_path].add(path)
    
    def remove_file(self, path: str) -> None:
        """
        Remove a file from the dependency graph.
        
        Args:
            path: File path to remove
        """
        if path not in self._nodes:
            return
        
        # Remove from dependencies
        if path in self._dependencies:
            for dep in self._dependencies[path]:
                if dep in self._dependents:
                    self._dependents[dep].discard(path)
            del self._dependencies[path]
        
        # Remove from dependents
        if path in self._dependents:
            for dependent in self._dependents[path]:
                if dependent in self._dependencies:
                    self._dependencies[dependent].discard(path)
            del self._dependents[path]
        
        # Remove node
        del self._nodes[path]
        
        # Clear import cache entries involving this file
        self._import_cache = {
            k: v for k, v in self._import_cache.items()
            if k[0] != path and v != path
        }
    
    def get_dependencies(self, path: str) -> Set[str]:
        """
        Get all files that the specified file depends on (imports).
        
        Args:
            path: File path
            
        Returns:
            Set of file paths that this file imports
        """
        return self._dependencies.get(path, set()).copy()
    
    def get_dependents(self, path: str) -> Set[str]:
        """
        Get all files that depend on the specified file (import it).
        
        Args:
            path: File path
            
        Returns:
            Set of file paths that import this file
        """
        return self._dependents.get(path, set()).copy()
    
    def get_transitive_dependencies(self, path: str) -> Set[str]:
        """
        Get all files that the specified file transitively depends on.
        
        This includes direct dependencies and all their dependencies recursively.
        
        Args:
            path: File path
            
        Returns:
            Set of all transitively dependent file paths
        """
        visited = set()
        to_visit = deque([path])
        
        while to_visit:
            current = to_visit.popleft()
            if current in visited:
                continue
            
            # Mark as visited but don't include the starting path in results
            visited.add(current)
            
            # Add dependencies of current file
            deps = self._dependencies.get(current, set())
            to_visit.extend(deps)
        
        # Remove the starting path from results
        visited.discard(path)
        return visited
    
    def get_transitive_dependents(self, path: str) -> Set[str]:
        """
        Get all files that transitively depend on the specified file.
        
        This includes direct dependents and all files that depend on them recursively.
        
        Args:
            path: File path
            
        Returns:
            Set of all files that transitively depend on this file
        """
        visited = set()
        to_visit = deque([path])
        
        while to_visit:
            current = to_visit.popleft()
            if current in visited:
                continue
            
            # Mark as visited but don't include the starting path in results
            visited.add(current)
            
            # Add dependents of current file
            deps = self._dependents.get(current, set())
            to_visit.extend(deps)
        
        # Remove the starting path from results
        visited.discard(path)
        return visited
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detect circular dependencies in the graph.
        
        Returns:
            List of cycles, where each cycle is a list of file paths forming a loop
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path_stack = []
        
        def dfs(node: str) -> None:
            """Depth-first search to detect cycles."""
            if node in rec_stack:
                # Found a cycle - extract it from path_stack
                cycle_start = path_stack.index(node)
                cycle = path_stack[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path_stack.append(node)
            
            # Visit all dependencies
            for dep in self._dependencies.get(node, set()):
                dfs(dep)
            
            path_stack.pop()
            rec_stack.remove(node)
        
        # Run DFS from each unvisited node
        for node in self._nodes:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def topological_sort(self) -> List[str]:
        """
        Perform topological sort on the dependency graph.
        
        Returns files in dependency order (dependencies before dependents).
        If cycles exist, returns partial ordering.
        
        Returns:
            List of file paths in topological order
        """
        # Count incoming edges (number of files this file imports)
        in_degree = {node: 0 for node in self._nodes}
        for node in self._nodes:
            for dep in self._dependencies.get(node, set()):
                if dep in in_degree:
                    in_degree[node] += 1
        
        # Start with nodes that have no dependencies
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Reduce in-degree for dependents
            for dependent in self._dependents.get(node, set()):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # If not all nodes are included, there are cycles
        if len(result) < len(self._nodes):
            logger.warning(
                f"Topological sort incomplete: {len(self._nodes) - len(result)} "
                f"nodes excluded due to cycles"
            )
            # Add remaining nodes (they're part of cycles)
            remaining = [n for n in self._nodes if n not in result]
            result.extend(remaining)
        
        return result
    
    def get_all_files(self) -> Set[str]:
        """
        Get all files in the dependency graph.
        
        Returns:
            Set of all file paths
        """
        return set(self._nodes.keys())
    
    def has_file(self, path: str) -> bool:
        """
        Check if a file exists in the dependency graph.
        
        Args:
            path: File path to check
            
        Returns:
            True if the file is in the graph
        """
        return path in self._nodes
    
    def get_node(self, path: str) -> Optional[DependencyNode]:
        """
        Get the dependency node for a file.
        
        Args:
            path: File path
            
        Returns:
            DependencyNode or None if not found
        """
        return self._nodes.get(path)
    
    def get_isolated_files(self) -> Set[str]:
        """
        Get files that have no dependencies and no dependents.
        
        Returns:
            Set of isolated file paths
        """
        isolated = set()
        for path in self._nodes:
            if (not self._dependencies.get(path) and 
                not self._dependents.get(path)):
                isolated.add(path)
        return isolated
    
    def get_leaf_files(self) -> Set[str]:
        """
        Get files that have no dependents (nothing imports them).
        
        These are typically entry points or unused files.
        
        Returns:
            Set of leaf file paths
        """
        leaves = set()
        for path in self._nodes:
            if not self._dependents.get(path):
                leaves.add(path)
        return leaves
    
    def get_root_files(self) -> Set[str]:
        """
        Get files that have no dependencies (import nothing).
        
        Returns:
            Set of root file paths
        """
        roots = set()
        for path in self._nodes:
            if not self._dependencies.get(path):
                roots.add(path)
        return roots
    
    def _resolve_import(
        self, 
        source_file: str, 
        import_name: str, 
        language: Optional[str]
    ) -> Optional[str]:
        """
        Resolve an import statement to an actual file path.
        
        Args:
            source_file: The file containing the import
            import_name: The import string (e.g., "module.submodule" or "./file")
            language: Programming language of the source file
            
        Returns:
            Resolved file path or None if it cannot be resolved
        """
        # Check cache first
        cache_key = (source_file, import_name)
        if cache_key in self._import_cache:
            return self._import_cache[cache_key]
        
        resolved = None
        
        if language == "python":
            resolved = self._resolve_python_import(source_file, import_name)
        elif language in ["javascript", "typescript", "jsx", "tsx"]:
            resolved = self._resolve_javascript_import(source_file, import_name)
        
        # Cache the result
        self._import_cache[cache_key] = resolved
        return resolved
    
    def _resolve_python_import(self, source_file: str, import_name: str) -> Optional[str]:
        """
        Resolve a Python import to a file path.
        
        Args:
            source_file: The file containing the import
            import_name: Python import name (e.g., "autodoc.core.state")
            
        Returns:
            Resolved file path or None
        """
        # Handle relative imports (start with .)
        if import_name.startswith("."):
            source_dir = str(Path(source_file).parent)
            
            # Count leading dots
            level = 0
            for char in import_name:
                if char == ".":
                    level += 1
                else:
                    break
            
            # Go up directories
            current_dir = Path(source_dir)
            for _ in range(level - 1):
                current_dir = current_dir.parent
            
            # Get the module part after the dots
            module_part = import_name[level:]
            if module_part:
                module_path = current_dir / module_part.replace(".", "/")
            else:
                module_path = current_dir
            
            # Try as a file or directory
            candidates = [
                str(module_path) + ".py",
                str(module_path / "__init__.py"),
            ]
        else:
            # Absolute import - try to find in known files
            module_path = import_name.replace(".", "/")
            candidates = [
                f"{module_path}.py",
                f"{module_path}/__init__.py",
            ]
        
        # Check if any candidate exists in our nodes
        for candidate in candidates:
            # Normalize path separators
            candidate = candidate.replace("\\", "/")
            if candidate in self._nodes:
                return candidate
        
        return None
    
    def _resolve_javascript_import(self, source_file: str, import_name: str) -> Optional[str]:
        """
        Resolve a JavaScript/TypeScript import to a file path.
        
        Args:
            source_file: The file containing the import
            import_name: Import path (e.g., "./file" or "module")
            
        Returns:
            Resolved file path or None
        """
        # Only handle relative imports (start with . or ..)
        if not (import_name.startswith("./") or import_name.startswith("../")):
            # Absolute imports from node_modules or similar - ignore
            return None
        
        source_dir = Path(source_file).parent
        target_path = (source_dir / import_name).resolve()
        
        # Try different extensions
        extensions = [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]
        candidates = [str(target_path)]
        
        # If no extension, try adding common extensions
        if not any(str(target_path).endswith(ext) for ext in extensions):
            candidates.extend([str(target_path) + ext for ext in extensions])
            # Also try index files
            candidates.extend([str(target_path / f"index{ext}") for ext in extensions])
        
        # Check if any candidate exists in our nodes
        for candidate in candidates:
            # Normalize path separators and make relative
            candidate = candidate.replace("\\", "/")
            if candidate in self._nodes:
                return candidate
        
        return None
    
    def to_dict(self) -> Dict[str, any]:
        """
        Serialize the dependency graph to a dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "nodes": {
                path: {
                    "imports": list(node.imports),
                    "language": node.language,
                }
                for path, node in self._nodes.items()
            },
            "dependencies": {
                path: list(deps)
                for path, deps in self._dependencies.items()
                if deps
            },
            "dependents": {
                path: list(deps)
                for path, deps in self._dependents.items()
                if deps
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "DependencyGraph":
        """
        Deserialize a dependency graph from a dictionary.
        
        Args:
            data: Dictionary representation from to_dict()
            
        Returns:
            DependencyGraph instance
        """
        graph = cls()
        
        # Restore nodes
        nodes_data = data.get("nodes", {})
        for path, node_data in nodes_data.items():
            graph.add_file(
                path=path,
                imports=set(node_data.get("imports", [])),
                language=node_data.get("language")
            )
        
        return graph
    
    def __len__(self) -> int:
        """Return the number of files in the graph."""
        return len(self._nodes)
    
    def __contains__(self, path: str) -> bool:
        """Check if a file is in the graph."""
        return path in self._nodes
    
    def __repr__(self) -> str:
        """Return string representation of the graph."""
        return f"DependencyGraph(files={len(self._nodes)}, dependencies={sum(len(d) for d in self._dependencies.values())})"

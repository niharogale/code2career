"""Analysis module for AST parsing, dependency graphs, and semantic change detection."""

from autodoc.analysis.ast_parser import (
    ASTParser,
    ParsedAST,
    Definition,
    DefinitionType,
)

from autodoc.analysis.dependency_graph import (
    DependencyGraph,
    DependencyNode,
)

from autodoc.analysis.semantic_changes import (
    SemanticChangeAnalyzer,
    SemanticChangeResult,
    ChangeCategory,
    DefinitionChange,
)

__all__ = [
    # AST Parser
    "ASTParser",
    "ParsedAST",
    "Definition",
    "DefinitionType",
    # Dependency Graph
    "DependencyGraph",
    "DependencyNode",
    # Semantic Changes
    "SemanticChangeAnalyzer",
    "SemanticChangeResult",
    "ChangeCategory",
    "DefinitionChange",
]

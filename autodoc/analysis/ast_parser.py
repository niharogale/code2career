"""AST Parser for multi-language code analysis using tree-sitter."""

import hashlib
from typing import Tuple, Set, List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    from tree_sitter import Language, Parser, Node, Tree
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Language = Any
    Parser = Any
    Node = Any
    Tree = Any


class DefinitionType(str, Enum):
    """Types of code definitions."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    INTERFACE = "interface"


@dataclass
class Definition:
    """Represents a code definition (function, class, method, etc.)."""
    name: str
    type: DefinitionType
    line: int
    is_public: bool = True
    parameters: Optional[List[str]] = None
    return_type: Optional[str] = None
    
    def __post_init__(self):
        """Initialize mutable default values."""
        if self.parameters is None:
            self.parameters = []


class ParsedAST:
    """Container for parsed AST information."""
    
    def __init__(self, tree: Optional[Tree], source_code: str):
        self.tree = tree
        self.source_code = source_code
        self.root_node = tree.root_node if tree else None
    
    def is_valid(self) -> bool:
        """Check if the AST was parsed successfully."""
        return self.tree is not None and self.root_node is not None


class ASTParser:
    """Multi-language AST parser using tree-sitter."""
    
    # Supported languages and their language functions
    SUPPORTED_LANGUAGES = {
        "python": tspython.language if TREE_SITTER_AVAILABLE else None,
        "javascript": tsjavascript.language if TREE_SITTER_AVAILABLE else None,
        "typescript": tsjavascript.language if TREE_SITTER_AVAILABLE else None,
        "jsx": tsjavascript.language if TREE_SITTER_AVAILABLE else None,
        "tsx": tsjavascript.language if TREE_SITTER_AVAILABLE else None,
    }
    
    @staticmethod
    def _get_language(language_func):
        """Call the language function to get the Language object."""
        if language_func is None:
            return None
        # The language functions return a PyCapsule that needs to be wrapped in Language
        return Language(language_func())
    
    def __init__(self, language: str):
        """
        Initialize the AST parser for a specific language.
        
        Args:
            language: Programming language (python, javascript, typescript, etc.)
        """
        if not TREE_SITTER_AVAILABLE:
            raise RuntimeError("tree-sitter is not installed. Install with: pip install tree-sitter tree-sitter-python tree-sitter-javascript")
        
        self.language = language.lower()
        
        # Get the language function
        ts_language_func = self.SUPPORTED_LANGUAGES.get(self.language)
        if ts_language_func is None:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(self.SUPPORTED_LANGUAGES.keys())}")
        
        # Get the Language object by calling the function
        self.ts_language = self._get_language(ts_language_func)
        if self.ts_language is None:
            raise ValueError(f"Failed to load language: {language}")
        
        # Initialize tree-sitter parser
        self.parser = Parser()
        self.parser.language = self.ts_language
    
    def parse(self, source_code: str) -> ParsedAST:
        """
        Parse source code into an AST.
        
        Args:
            source_code: The source code to parse
            
        Returns:
            ParsedAST object containing the parsed tree
        """
        try:
            # Parse the source code
            tree = self.parser.parse(bytes(source_code, "utf8"))
            return ParsedAST(tree, source_code)
        except Exception as e:
            # Return invalid AST on parse error
            return ParsedAST(None, source_code)
    
    def extract_definitions(self, ast: ParsedAST) -> List[Definition]:
        """
        Extract function, class, and method definitions from AST.
        
        Args:
            ast: Parsed AST
            
        Returns:
            List of Definition objects
        """
        if not ast.is_valid():
            return []
        
        definitions = []
        
        if self.language == "python":
            definitions = self._extract_python_definitions(ast)
        elif self.language in ["javascript", "typescript", "jsx", "tsx"]:
            definitions = self._extract_javascript_definitions(ast)
        
        return definitions
    
    def extract_imports(self, ast: ParsedAST) -> Set[str]:
        """
        Extract import statements from AST.
        
        Args:
            ast: Parsed AST
            
        Returns:
            Set of imported module/file names
        """
        if not ast.is_valid():
            return set()
        
        imports = set()
        
        if self.language == "python":
            imports = self._extract_python_imports(ast)
        elif self.language in ["javascript", "typescript", "jsx", "tsx"]:
            imports = self._extract_javascript_imports(ast)
        
        return imports
    
    def compute_ast_hash(self, ast: ParsedAST) -> str:
        """
        Generate a stable hash of the AST structure.
        
        This hash ignores comments, whitespace, and other non-semantic elements.
        
        Args:
            ast: Parsed AST
            
        Returns:
            Hash string (hex digest)
        """
        if not ast.is_valid():
            # Fall back to source code hash if AST parsing failed
            return f"source:{hashlib.sha256(ast.source_code.encode()).hexdigest()[:16]}"
        
        # Store source code temporarily for node text extraction
        self._current_source = ast.source_code
        
        # Get structural representation of AST
        ast_structure = self._get_ast_structure(ast.root_node)
        
        # Clean up temporary reference
        delattr(self, '_current_source')
        
        # Compute hash
        hash_obj = hashlib.sha256(ast_structure.encode())
        return f"ast:{hash_obj.hexdigest()[:16]}"
    
    def _get_ast_structure(self, node: Node, depth: int = 0) -> str:
        """
        Get a string representation of the AST structure.
        
        This ignores comments and focuses on semantic structure.
        Includes identifiers and important literal values for better differentiation.
        """
        if node is None:
            return ""
        
        # Skip comment nodes
        if "comment" in node.type.lower():
            return ""
        
        # Build structure string
        parts = [f"{node.type}"]
        
        # For identifier nodes, include the actual identifier name
        if node.type == "identifier":
            text = self._get_node_text(node)
            if text:
                parts.append(f"'{text}'")
        
        # For string literals, include a content indicator (not full string for brevity)
        elif node.type in ["string", "string_literal", "string_content"]:
            text = self._get_node_text(node)
            if text:
                # Include a hash of the string content
                content_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
                parts.append(f"str:{content_hash}")
        
        # For named nodes, recursively process children
        if node.is_named:
            for child in node.children:
                child_structure = self._get_ast_structure(child, depth + 1)
                if child_structure:
                    parts.append(child_structure)
        
        return "(" + ",".join(parts) + ")"
    
    def _get_node_text(self, node: Node) -> str:
        """Get the text content of a node from the source code."""
        if hasattr(self, '_current_source'):
            return self._current_source[node.start_byte:node.end_byte]
        return ""
    
    def _extract_python_definitions(self, ast: ParsedAST) -> List[Definition]:
        """Extract definitions from Python AST."""
        definitions = []
        
        def visit_node(node: Node):
            if node.type == "function_definition":
                # Extract function name
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = ast.source_code[name_node.start_byte:name_node.end_byte]
                    line = node.start_point[0] + 1
                    is_public = not name.startswith("_")
                    
                    # Extract parameters
                    parameters = []
                    return_type = None
                    params_node = node.child_by_field_name("parameters")
                    if params_node:
                        for child in params_node.children:
                            if child.type == "identifier":
                                param_name = ast.source_code[child.start_byte:child.end_byte]
                                parameters.append(param_name)
                            elif child.type == "typed_parameter":
                                # Extract parameter with type annotation
                                param_name_node = child.child_by_field_name("name") or child.children[0]
                                if param_name_node and param_name_node.type == "identifier":
                                    param_name = ast.source_code[param_name_node.start_byte:param_name_node.end_byte]
                                    type_node = child.child_by_field_name("type")
                                    if type_node:
                                        param_type = ast.source_code[type_node.start_byte:type_node.end_byte]
                                        parameters.append(f"{param_name}: {param_type}")
                                    else:
                                        parameters.append(param_name)
                            elif child.type == "default_parameter":
                                # Extract parameter with default value
                                param_name_node = child.child_by_field_name("name")
                                if param_name_node:
                                    param_name = ast.source_code[param_name_node.start_byte:param_name_node.end_byte]
                                    parameters.append(f"{param_name}=...")
                    
                    # Extract return type
                    return_type_node = node.child_by_field_name("return_type")
                    if return_type_node:
                        return_type = ast.source_code[return_type_node.start_byte:return_type_node.end_byte]
                    
                    definitions.append(Definition(
                        name=name,
                        type=DefinitionType.FUNCTION,
                        line=line,
                        is_public=is_public,
                        parameters=parameters,
                        return_type=return_type
                    ))
            
            elif node.type == "class_definition":
                # Extract class name
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = ast.source_code[name_node.start_byte:name_node.end_byte]
                    line = node.start_point[0] + 1
                    is_public = not name.startswith("_")
                    definitions.append(Definition(
                        name=name,
                        type=DefinitionType.CLASS,
                        line=line,
                        is_public=is_public
                    ))
            
            # Recursively visit children
            for child in node.children:
                visit_node(child)
        
        visit_node(ast.root_node)
        return definitions
    
    def _extract_javascript_definitions(self, ast: ParsedAST) -> List[Definition]:
        """Extract definitions from JavaScript/TypeScript AST."""
        definitions = []
        
        def visit_node(node: Node):
            if node.type in ["function_declaration", "function"]:
                # Extract function name
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = ast.source_code[name_node.start_byte:name_node.end_byte]
                    line = node.start_point[0] + 1
                    
                    # Extract parameters
                    parameters = []
                    return_type = None
                    params_node = node.child_by_field_name("parameters")
                    if params_node:
                        for child in params_node.children:
                            if child.type == "identifier":
                                param_name = ast.source_code[child.start_byte:child.end_byte]
                                parameters.append(param_name)
                            elif child.type == "required_parameter":
                                # TypeScript typed parameter
                                param_name_node = child.child_by_field_name("pattern")
                                if param_name_node:
                                    param_name = ast.source_code[param_name_node.start_byte:param_name_node.end_byte]
                                    type_node = child.child_by_field_name("type")
                                    if type_node:
                                        param_type = ast.source_code[type_node.start_byte:type_node.end_byte]
                                        parameters.append(f"{param_name}: {param_type}")
                                    else:
                                        parameters.append(param_name)
                            elif child.type == "optional_parameter":
                                # TypeScript optional parameter
                                param_name_node = child.child_by_field_name("pattern")
                                if param_name_node:
                                    param_name = ast.source_code[param_name_node.start_byte:param_name_node.end_byte]
                                    parameters.append(f"{param_name}?")
                    
                    # Extract return type (TypeScript)
                    return_type_node = node.child_by_field_name("return_type")
                    if return_type_node:
                        return_type = ast.source_code[return_type_node.start_byte:return_type_node.end_byte]
                    
                    definitions.append(Definition(
                        name=name,
                        type=DefinitionType.FUNCTION,
                        line=line,
                        is_public=True,  # JS doesn't have private by convention
                        parameters=parameters,
                        return_type=return_type
                    ))
            
            elif node.type == "class_declaration":
                # Extract class name
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = ast.source_code[name_node.start_byte:name_node.end_byte]
                    line = node.start_point[0] + 1
                    definitions.append(Definition(
                        name=name,
                        type=DefinitionType.CLASS,
                        line=line,
                        is_public=True
                    ))
            
            elif node.type == "method_definition":
                # Extract method name
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = ast.source_code[name_node.start_byte:name_node.end_byte]
                    line = node.start_point[0] + 1
                    is_public = not name.startswith("_")
                    
                    # Extract parameters
                    parameters = []
                    return_type = None
                    params_node = node.child_by_field_name("parameters")
                    if params_node:
                        for child in params_node.children:
                            if child.type == "identifier":
                                param_name = ast.source_code[child.start_byte:child.end_byte]
                                parameters.append(param_name)
                            elif child.type == "required_parameter":
                                param_name_node = child.child_by_field_name("pattern")
                                if param_name_node:
                                    param_name = ast.source_code[param_name_node.start_byte:param_name_node.end_byte]
                                    parameters.append(param_name)
                    
                    # Extract return type
                    return_type_node = node.child_by_field_name("return_type")
                    if return_type_node:
                        return_type = ast.source_code[return_type_node.start_byte:return_type_node.end_byte]
                    
                    definitions.append(Definition(
                        name=name,
                        type=DefinitionType.METHOD,
                        line=line,
                        is_public=is_public,
                        parameters=parameters,
                        return_type=return_type
                    ))
            
            elif node.type in ["variable_declaration", "lexical_declaration"]:
                # Extract const/let/var declarations
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name")
                        if name_node:
                            name = ast.source_code[name_node.start_byte:name_node.end_byte]
                            line = child.start_point[0] + 1
                            definitions.append(Definition(
                                name=name,
                                type=DefinitionType.VARIABLE,
                                line=line,
                                is_public=True
                            ))
            
            # Recursively visit children
            for child in node.children:
                visit_node(child)
        
        visit_node(ast.root_node)
        return definitions
    
    def _extract_python_imports(self, ast: ParsedAST) -> Set[str]:
        """Extract imports from Python AST."""
        imports = set()
        
        def visit_node(node: Node):
            if node.type == "import_statement":
                # import module
                for child in node.children:
                    if child.type == "dotted_name":
                        module = ast.source_code[child.start_byte:child.end_byte]
                        imports.add(module)
            
            elif node.type == "import_from_statement":
                # from module import name
                module_node = node.child_by_field_name("module_name")
                if module_node:
                    module = ast.source_code[module_node.start_byte:module_node.end_byte]
                    imports.add(module)
            
            # Recursively visit children
            for child in node.children:
                visit_node(child)
        
        visit_node(ast.root_node)
        return imports
    
    def _extract_javascript_imports(self, ast: ParsedAST) -> Set[str]:
        """Extract imports from JavaScript/TypeScript AST."""
        imports = set()
        
        def visit_node(node: Node):
            if node.type == "import_statement":
                # import ... from 'module'
                source_node = node.child_by_field_name("source")
                if source_node:
                    # Remove quotes from string literal
                    module = ast.source_code[source_node.start_byte:source_node.end_byte]
                    module = module.strip('"\'')
                    imports.add(module)
            
            elif node.type == "import_clause":
                # Handle import clauses
                pass
            
            # Recursively visit children
            for child in node.children:
                visit_node(child)
        
        visit_node(ast.root_node)
        return imports
    
    @staticmethod
    def is_supported_language(language: str) -> bool:
        """Check if a language is supported for AST parsing."""
        return language.lower() in ASTParser.SUPPORTED_LANGUAGES
    
    @staticmethod
    def get_language_from_extension(extension: str) -> Optional[str]:
        """
        Get the language name from a file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.js')
            
        Returns:
            Language name or None if not supported
        """
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".mjs": "javascript",
            ".cjs": "javascript",
        }
        return extension_map.get(extension.lower())

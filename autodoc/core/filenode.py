from dataclasses import dataclass
from typing import Set

@dataclass
class FileNode:
    path: str
    language: str
    ast_hash: str
    imports: Set[str]

    def is_dirty(self, new_ast_hash: str) -> bool:
        """
        Returns True if the AST has changed.
        """
        # TODO: implement comparison logic
        # TODO: Decde how to normalize hashes
        # TODO: Decide what "equal" means
        pass
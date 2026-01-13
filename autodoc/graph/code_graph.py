from typing import Dict, Set

class CodeGraph:
    def __init__(self):
        self.edges: Dict[str, Set[str]] = {}

    def add_file(self, file_path: str):
        if file_path not in self.edges:
            self.edges[file_path] = set()

    def add_dependency(self, src: str, dst: str):
        """
        src depends on dst
        """
        # TODO: add edge
        pass

    def get_dependencies(self, file_path: str) -> Set[str]:
        return self.edges.get(file_path, set())
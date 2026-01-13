import os
from typing import List

SOURCE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
}

IGNORE_NAMES = {
    ".git",
    "venv",
    "node_modules",
    "__pycache__",
}

def scan_repo(root: str) -> List[str]:
    """
    Walk the repository and return a list of source file paths.
    """
    source_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        # TODO: ignore .git, venv, node_modules

        dirnames[:] = [d for d in dirnames if d not in IGNORE_NAMES]

        for f in filenames:
            ext = os.path.splitext(f)[1]
            if ext in SOURCE_EXTENSIONS:
                full_path = os.path.join(dirpath, f)
                source_files.append(os.path.join(dirpath, f))

    source_files.sort()
    return source_files


if __name__ == "__main__":
    files = scan_repo("test_repo")
    print(len(files))
    for f in files:
        print(f)

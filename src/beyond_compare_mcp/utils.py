"""Utility functions for Beyond Compare MCP Server"""

import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Any


def validate_path(path: str, must_exist: bool = True) -> tuple[bool, str]:
    """
    Validate a file or directory path.

    Args:
        path: Path to validate
        must_exist: Whether the path must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path_obj = Path(path).resolve()

        if must_exist and not path_obj.exists():
            return False, f"Path does not exist: {path}"

        # Check if path is accessible
        if path_obj.exists():
            try:
                # Try to access the path
                if path_obj.is_file():
                    path_obj.stat()
                elif path_obj.is_dir():
                    list(path_obj.iterdir())
            except PermissionError:
                return False, f"Permission denied: {path}"
            except Exception as e:
                return False, f"Cannot access path: {path} ({str(e)})"

        return True, ""

    except Exception as e:
        return False, f"Invalid path: {path} ({str(e)})"


def get_file_info(file_path: str) -> dict[str, Any]:
    """
    Get detailed information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {"error": "File does not exist"}

        stat_info = path_obj.stat()

        info = {
            "path": str(path_obj.resolve()),
            "name": path_obj.name,
            "size": stat_info.st_size,
            "modified": stat_info.st_mtime,
            "created": stat_info.st_ctime,
            "is_file": path_obj.is_file(),
            "is_directory": path_obj.is_dir(),
            "is_symlink": path_obj.is_symlink(),
            "permissions": oct(stat_info.st_mode)[-3:],
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK),
            "executable": os.access(file_path, os.X_OK),
        }

        if path_obj.is_file():
            # Add file-specific information
            info["extension"] = path_obj.suffix.lower()
            info["mime_type"] = mimetypes.guess_type(file_path)[0]

            # Calculate file hash for small files
            if stat_info.st_size < 10 * 1024 * 1024:  # 10MB
                try:
                    with open(file_path, "rb") as f:
                        info["md5_hash"] = hashlib.md5(f.read()).hexdigest()
                except Exception:
                    info["md5_hash"] = None

        return info

    except Exception as e:
        return {"error": f"Cannot get file info: {str(e)}"}


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def find_files_by_pattern(
    directory: str, pattern: str, recursive: bool = True
) -> list[str]:
    """
    Find files matching a pattern in a directory.

    Args:
        directory: Directory to search in
        pattern: File pattern (e.g., "*.py", "test_*.txt")
        recursive: Whether to search recursively

    Returns:
        List of matching file paths
    """

    matches = []
    path_obj = Path(directory)

    if not path_obj.exists() or not path_obj.is_dir():
        return matches

    try:
        if recursive:
            for file_path in path_obj.rglob(pattern):
                if file_path.is_file():
                    matches.append(str(file_path))
        else:
            for file_path in path_obj.glob(pattern):
                if file_path.is_file():
                    matches.append(str(file_path))

    except Exception:
        pass

    return sorted(matches)


def create_backup(file_path: str, backup_suffix: str = ".bak") -> str | None:
    """
    Create a backup of a file.

    Args:
        file_path: Path to the file to backup
        backup_suffix: Suffix for backup file

    Returns:
        Path to backup file or None if failed
    """
    try:
        path_obj = Path(file_path)
        if not path_obj.exists() or not path_obj.is_file():
            return None

        backup_path = str(path_obj) + backup_suffix

        # If backup already exists, add a number
        counter = 1
        while os.path.exists(backup_path):
            backup_path = f"{str(path_obj)}{backup_suffix}.{counter}"
            counter += 1

        # Copy the file
        import shutil

        shutil.copy2(file_path, backup_path)

        return backup_path

    except Exception:
        return None


def normalize_path(path: str) -> str:
    """
    Normalize a file path for cross-platform compatibility.

    Args:
        path: Path to normalize

    Returns:
        Normalized path
    """
    return str(Path(path).resolve())


def is_binary_file(file_path: str, chunk_size: int = 1024) -> bool:
    """
    Check if a file is binary by examining its content.

    Args:
        file_path: Path to the file
        chunk_size: Size of chunk to read for analysis

    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(chunk_size)

        # Check for null bytes (common in binary files)
        if b"\x00" in chunk:
            return True

        # Check for high ratio of non-printable characters
        printable_chars = sum(
            1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13]
        )
        if len(chunk) > 0 and printable_chars / len(chunk) < 0.7:
            return True

        return False

    except Exception:
        return True  # Assume binary if we can't read it

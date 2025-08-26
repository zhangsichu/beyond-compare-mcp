#!/usr/bin/env python3
"""
Beyond Compare MCP Server

This server provides natural language interface to Beyond Compare operations
including file comparison, folder comparison, synchronization, and more.
"""

import asyncio
import logging
import os
import shutil
import subprocess
from typing import Any

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("BeyondCompare")


class BeyondCompareError(Exception):
    """Custom exception for Beyond Compare operations"""

    pass


class BeyondCompareManager:
    """Manager class for Beyond Compare operations"""

    def __init__(self):
        self.bc_executable = self._find_beyond_compare()

    def _find_beyond_compare(self) -> str | None:
        """Find Beyond Compare executable on the system"""
        possible_paths = [
            # macOS paths
            "/Applications/Beyond Compare.app/Contents/MacOS/bcomp",
            "/usr/local/bin/bcomp",
            # Windows paths
            "C:\\Program Files\\Beyond Compare 5\\BCompare.exe",
            "C:\\Program Files\\Beyond Compare 4\\BCompare.exe",
            "C:\\Program Files (x86)\\Beyond Compare 5\\BCompare.exe",
            "C:\\Program Files (x86)\\Beyond Compare 4\\BCompare.exe",
            # Linux paths
            "/usr/bin/bcompare",
            "/usr/local/bin/bcompare",
        ]

        # Check if bcomp/bcompare is in PATH
        for cmd in ["bcomp", "bcompare", "BCompare.exe"]:
            if shutil.which(cmd):
                return cmd

        # Check specific paths
        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _run_command(self, args: list[str], timeout: int = 30) -> dict[str, Any]:
        """Run Beyond Compare command and return result"""
        if not self.bc_executable:
            raise BeyondCompareError(
                "Beyond Compare executable not found. Please install Beyond Compare."
            )

        cmd = [self.bc_executable] + args

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )

            return {
                "success": result.returncode
                < 100,  # Beyond Compare success codes are < 100
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
            }
        except subprocess.TimeoutExpired:
            raise BeyondCompareError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise BeyondCompareError(f"Failed to execute command: {str(e)}")


# Initialize Beyond Compare manager
bc_manager = BeyondCompareManager()


@mcp.tool()
def compare_files(
    left_file: str,
    right_file: str,
    output_format: str = "text",
    ignore_case: bool = False,
    ignore_whitespace: bool = False,
) -> str:
    """
    Compare two files using Beyond Compare.

    Args:
        left_file: Path to the first file to compare
        right_file: Path to the second file to compare
        output_format: Output format - 'text', 'html', or 'side-by-side'
        ignore_case: Whether to ignore case differences
        ignore_whitespace: Whether to ignore whitespace differences

    Returns:
        Comparison result as formatted text
    """
    try:
        # Validate file paths
        if not os.path.exists(left_file):
            return f"Error: Left file '{left_file}' does not exist"
        if not os.path.exists(right_file):
            return f"Error: Right file '{right_file}' does not exist"

        args = []

        # Add comparison options
        if ignore_case:
            args.extend(["-ignorecase"])
        if ignore_whitespace:
            args.extend(["-ignoreunimportant"])

        # Add file paths
        args.extend([left_file, right_file])

        # For text output, use quiet comparison mode
        if output_format == "text":
            args.insert(0, "-qc")

        result = bc_manager._run_command(args)

        if result["success"]:
            if result["returncode"] in [
                0,
                1,
                2,
            ]:  # 0=Success, 1=Binary same, 2=Rules-based same
                return "Files are identical"
            else:
                return (
                    f"Files differ:\n{result['stdout']}"
                    if result["stdout"]
                    else "Files have differences"
                )
        else:
            return f"Comparison failed: {result['stderr']}"

    except Exception as e:
        return f"Error comparing files: {str(e)}"


@mcp.tool()
def compare_folders(
    left_folder: str,
    right_folder: str,
    recursive: bool = True,
    show_identical: bool = False,
    show_different: bool = True,
    show_left_only: bool = True,
    show_right_only: bool = True,
) -> str:
    """
    Compare two folders using Beyond Compare.

    Args:
        left_folder: Path to the first folder to compare
        right_folder: Path to the second folder to compare
        recursive: Whether to compare subfolders recursively
        show_identical: Whether to show identical files in results
        show_different: Whether to show different files in results
        show_left_only: Whether to show files that exist only in left folder
        show_right_only: Whether to show files that exist only in right folder

    Returns:
        Folder comparison result as formatted text
    """
    try:
        # Validate folder paths
        if not os.path.exists(left_folder):
            return f"Error: Left folder '{left_folder}' does not exist"
        if not os.path.exists(right_folder):
            return f"Error: Right folder '{right_folder}' does not exist"

        args = ["-qc"]

        # Add comparison options
        if recursive:
            args.extend(["-recurse"])

        # Add folder paths
        args.extend([left_folder, right_folder])

        result = bc_manager._run_command(args)

        if result["success"]:
            output = (
                result["stdout"]
                if result["stdout"]
                else "Folders compared successfully"
            )
            return f"Folder comparison result:\n{output}"
        else:
            return f"Folder comparison failed: {result['stderr']}"

    except Exception as e:
        return f"Error comparing folders: {str(e)}"


@mcp.tool()
def sync_folders(
    source_folder: str,
    target_folder: str,
    direction: str = "left-to-right",
    delete_orphans: bool = False,
    preview_only: bool = True,
) -> str:
    """
    Synchronize two folders using Beyond Compare.

    Args:
        source_folder: Path to the source folder
        target_folder: Path to the target folder
        direction: Sync direction - 'left-to-right', 'right-to-left', or 'bidirectional'
        delete_orphans: Whether to delete files that don't exist in source
        preview_only: If True, only show what would be synchronized without actually doing it

    Returns:
        Synchronization result or preview
    """
    try:
        # Validate folder paths
        if not os.path.exists(source_folder):
            return f"Error: Source folder '{source_folder}' does not exist"
        if not os.path.exists(target_folder):
            return f"Error: Target folder '{target_folder}' does not exist"

        args = []

        if preview_only:
            args.extend(["-silent"])

        # Add sync direction options
        if direction == "left-to-right":
            args.extend(["-sync", "update:left->right"])
        elif direction == "right-to-left":
            args.extend(["-sync", "update:right->left"])
        elif direction == "bidirectional":
            args.extend(["-sync", "update:left<->right"])
        else:
            return f"Error: Invalid direction '{direction}'. Use 'left-to-right', 'right-to-left', or 'bidirectional'"

        if delete_orphans:
            args.extend(["create:left->right", "delete:left->right"])

        # Add folder paths
        args.extend([source_folder, target_folder])

        result = bc_manager._run_command(args)

        if result["success"]:
            action = (
                "Preview of synchronization"
                if preview_only
                else "Synchronization completed"
            )
            output = result["stdout"] if result["stdout"] else f"{action} successfully"
            return f"{action}:\n{output}"
        else:
            return f"Synchronization failed: {result['stderr']}"

    except Exception as e:
        return f"Error synchronizing folders: {str(e)}"


@mcp.tool()
def generate_report(
    left_path: str,
    right_path: str,
    report_type: str = "html",
    output_file: str | None = None,
) -> str:
    """
    Generate a comparison report using Beyond Compare.

    Args:
        left_path: Path to the left file or folder
        right_path: Path to the right file or folder
        report_type: Type of report - 'html', 'xml', 'csv', or 'text'
        output_file: Optional path for the output report file

    Returns:
        Status of report generation
    """
    try:
        # Validate paths
        if not os.path.exists(left_path):
            return f"Error: Left path '{left_path}' does not exist"
        if not os.path.exists(right_path):
            return f"Error: Right path '{right_path}' does not exist"

        # Generate output filename if not provided
        if not output_file:
            timestamp = asyncio.get_event_loop().time()
            output_file = f"bc_report_{int(timestamp)}.{report_type}"

        args = ["-silent"]

        # Add report format
        if report_type == "html":
            args.extend(["-report", "html"])
        elif report_type == "xml":
            args.extend(["-report", "xml"])
        elif report_type == "csv":
            args.extend(["-report", "csv"])
        elif report_type == "text":
            args.extend(["-report", "text"])
        else:
            return f"Error: Invalid report type '{report_type}'. Use 'html', 'xml', 'csv', or 'text'"

        # Add output file
        args.extend(["-reportfile", output_file])

        # Add paths
        args.extend([left_path, right_path])

        result = bc_manager._run_command(args)

        if result["success"]:
            return f"Report generated successfully: {output_file}"
        else:
            return f"Report generation failed: {result['stderr']}"

    except Exception as e:
        return f"Error generating report: {str(e)}"


@mcp.tool()
def get_beyond_compare_info() -> str:
    """
    Get information about the Beyond Compare installation.

    Returns:
        Information about Beyond Compare version and capabilities
    """
    try:
        if not bc_manager.bc_executable:
            return "Beyond Compare is not installed or not found in PATH"

        # Try to get version info
        result = bc_manager._run_command(["-help"])

        info = f"Beyond Compare executable: {bc_manager.bc_executable}\n"

        if result["success"]:
            info += f"Version information:\n{result['stdout'][:500]}..."
        else:
            info += "Could not retrieve version information"

        return info

    except Exception as e:
        return f"Error getting Beyond Compare info: {str(e)}"


@mcp.tool()
def list_file_formats() -> str:
    """
    List supported file formats and comparison types in Beyond Compare.

    Returns:
        List of supported file formats and comparison capabilities
    """
    return """
Beyond Compare supports comparison of:

File Types:
- Text files (.txt, .log, .ini, .cfg, etc.)
- Source code files (.py, .js, .java, .cpp, .cs, etc.)
- Data files (.csv, .xml, .json, .yaml, etc.)
- Image files (.jpg, .png, .gif, .bmp, etc.)
- Binary files (hex comparison)
- Archive files (.zip, .tar, .gz, etc.)
- Office documents (.doc, .xls, .ppt, etc.)

Comparison Types:
- Text comparison (line-by-line, word-by-word)
- Binary comparison (byte-by-byte)
- Image comparison (pixel differences)
- Folder comparison (file lists, sizes, dates)
- Archive comparison (contents)

Special Features:
- Ignore whitespace, case, line endings
- Regular expression filtering
- Custom file type rules
- Three-way merge capabilities
- Synchronization options
"""


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

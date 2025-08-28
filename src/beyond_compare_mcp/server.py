#!/usr/bin/env python3
"""
Beyond Compare MCP Server

This server provides tools for file and folder comparison, merging, and synchronization
using Beyond Compare command line interface.
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging to stderr (not stdout for MCP)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("beyond-compare-mcp")

# Initialize FastMCP server
mcp = FastMCP("beyond-compare")

# Beyond Compare executable paths for different platforms
BCOMPARE_PATHS = {
    "darwin": [
        "/Applications/Beyond Compare.app/Contents/MacOS/bcomp",
        "/usr/local/bin/bcomp",
        "bcomp"
    ],
    "win32": [
        "C:\\Program Files\\Beyond Compare 5\\BComp.exe",
        "C:\\Program Files\\Beyond Compare 4\\BComp.exe", 
        "C:\\Program Files (x86)\\Beyond Compare 5\\BComp.exe",
        "C:\\Program Files (x86)\\Beyond Compare 4\\BComp.exe",
        "bcomp.exe"
    ],
    "linux": [
        "/usr/bin/bcomp",
        "/usr/local/bin/bcomp",
        "bcomp"
    ]
}


class ComparisonResult(BaseModel):
    """Result of a Beyond Compare operation"""
    success: bool
    exit_code: int
    output: str
    error: str = ""
    report_path: Optional[str] = None


def find_bcompare_executable() -> Optional[str]:
    """Find the Beyond Compare executable on the system"""
    platform = sys.platform
    paths = BCOMPARE_PATHS.get(platform, BCOMPARE_PATHS["linux"])
    
    for path in paths:
        if shutil.which(path) or os.path.exists(path):
            logger.info(f"Found Beyond Compare at: {path}")
            return path
    
    logger.warning("Beyond Compare executable not found")
    return None


async def run_bcompare_command(args: List[str]) -> ComparisonResult:
    """Run a Beyond Compare command asynchronously"""
    bcomp_path = find_bcompare_executable()
    if not bcomp_path:
        return ComparisonResult(
            success=False,
            exit_code=-1,
            output="",
            error="Beyond Compare executable not found. Please install Beyond Compare."
        )
    
    cmd = [bcomp_path] + args
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return ComparisonResult(
            success=process.returncode == 0,
            exit_code=process.returncode or 0,
            output=stdout.decode('utf-8', errors='ignore'),
            error=stderr.decode('utf-8', errors='ignore')
        )
        
    except Exception as e:
        logger.error(f"Error running Beyond Compare command: {e}")
        return ComparisonResult(
            success=False,
            exit_code=-1,
            output="",
            error=f"Failed to execute Beyond Compare: {str(e)}"
        )


def validate_path(path: str) -> bool:
    """Validate that a path exists and is accessible"""
    try:
        return Path(path).exists()
    except Exception:
        return False


@mcp.tool()
async def compare_files(left_file: str, right_file: str, output_format: str = "text") -> str:
    """Compare two files using Beyond Compare.
    
    Args:
        left_file: Path to the first file to compare
        right_file: Path to the second file to compare
        output_format: Output format - "text" for console output, "html" for HTML report
    
    Returns:
        Comparison result with differences highlighted
    """
    if not validate_path(left_file):
        return f"Error: Left file does not exist: {left_file}"
    
    if not validate_path(right_file):
        return f"Error: Right file does not exist: {right_file}"
    
    args = [left_file, right_file]
    
    # Add format-specific arguments
    if output_format.lower() == "html":
        # Generate HTML report
        report_path = f"/tmp/bc_report_{os.getpid()}.html"
        args.extend(["-report", report_path, "-outputformat", "html"])
        
        result = await run_bcompare_command(args)
        
        if result.success and os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report_content = f.read()
            os.unlink(report_path)  # Clean up
            return f"File comparison completed successfully.\n\nHTML Report:\n{report_content}"
        else:
            return f"Comparison failed: {result.error or 'Unknown error'}"
    else:
        # Text output
        args.extend(["-silent"])
        result = await run_bcompare_command(args)
        
        if result.exit_code == 0:
            return f"Files are identical: {left_file} and {right_file}"
        elif result.exit_code == 1:
            return f"Files are different: {left_file} and {right_file}\n\nDetails:\n{result.output}"
        else:
            return f"Comparison failed (exit code {result.exit_code}): {result.error}"


@mcp.tool()
async def compare_folders(left_folder: str, right_folder: str, include_subdirs: bool = True) -> str:
    """Compare two folders using Beyond Compare.
    
    Args:
        left_folder: Path to the first folder to compare
        right_folder: Path to the second folder to compare
        include_subdirs: Whether to include subdirectories in comparison
    
    Returns:
        Folder comparison summary with differences
    """
    if not validate_path(left_folder):
        return f"Error: Left folder does not exist: {left_folder}"
    
    if not validate_path(right_folder):
        return f"Error: Right folder does not exist: {right_folder}"
    
    args = [left_folder, right_folder, "-silent"]
    
    if not include_subdirs:
        args.append("-nosubdirs")
    
    result = await run_bcompare_command(args)
    
    if result.exit_code == 0:
        return f"Folders are identical: {left_folder} and {right_folder}"
    elif result.exit_code == 1:
        return f"Folders have differences: {left_folder} and {right_folder}\n\nSummary:\n{result.output}"
    else:
        return f"Folder comparison failed (exit code {result.exit_code}): {result.error}"


@mcp.tool()
async def generate_comparison_report(left_path: str, right_path: str, report_path: str, report_format: str = "html") -> str:
    """Generate a detailed comparison report.
    
    Args:
        left_path: Path to the first file or folder to compare
        right_path: Path to the second file or folder to compare
        report_path: Path where to save the comparison report
        report_format: Report format - "html", "xml", or "text"
    
    Returns:
        Status of report generation
    """
    if not validate_path(left_path):
        return f"Error: Left path does not exist: {left_path}"
    
    if not validate_path(right_path):
        return f"Error: Right path does not exist: {right_path}"
    
    # Ensure report directory exists
    report_dir = os.path.dirname(report_path)
    if report_dir and not os.path.exists(report_dir):
        os.makedirs(report_dir, exist_ok=True)
    
    args = [
        left_path, right_path,
        "-report", report_path,
        "-outputformat", report_format.lower()
    ]
    
    result = await run_bcompare_command(args)
    
    if result.success and os.path.exists(report_path):
        file_size = os.path.getsize(report_path)
        return f"Comparison report generated successfully at {report_path} ({file_size} bytes)"
    else:
        return f"Failed to generate report: {result.error or 'Unknown error'}"


@mcp.tool()
async def sync_folders(source_folder: str, target_folder: str, sync_mode: str = "mirror") -> str:
    """Synchronize two folders using Beyond Compare.
    
    Args:
        source_folder: Source folder path
        target_folder: Target folder path  
        sync_mode: Sync mode - "mirror" (make target identical to source), "update" (copy newer files only)
    
    Returns:
        Synchronization result
    """
    if not validate_path(source_folder):
        return f"Error: Source folder does not exist: {source_folder}"
    
    # Create target folder if it doesn't exist
    if not os.path.exists(target_folder):
        try:
            os.makedirs(target_folder, exist_ok=True)
        except Exception as e:
            return f"Error: Cannot create target folder {target_folder}: {e}"
    
    args = [source_folder, target_folder]
    
    if sync_mode.lower() == "mirror":
        args.extend(["-sync", "-mirror"])
    elif sync_mode.lower() == "update":
        args.extend(["-sync", "-update"])
    else:
        return f"Error: Invalid sync mode '{sync_mode}'. Use 'mirror' or 'update'"
    
    result = await run_bcompare_command(args)
    
    if result.success:
        return f"Folder synchronization completed successfully from {source_folder} to {target_folder}"
    else:
        return f"Synchronization failed: {result.error or 'Unknown error'}"


@mcp.tool()
async def merge_files(left_file: str, right_file: str, output_file: str, base_file: Optional[str] = None) -> str:
    """Merge two or three files using Beyond Compare.
    
    Args:
        left_file: Path to the left file
        right_file: Path to the right file  
        output_file: Path where to save the merged result
        base_file: Optional path to base file for 3-way merge
    
    Returns:
        Merge operation result
    """
    if not validate_path(left_file):
        return f"Error: Left file does not exist: {left_file}"
    
    if not validate_path(right_file):
        return f"Error: Right file does not exist: {right_file}"
    
    if base_file and not validate_path(base_file):
        return f"Error: Base file does not exist: {base_file}"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    if base_file:
        # 3-way merge
        args = [left_file, right_file, base_file, output_file, "-automerge"]
    else:
        # 2-way merge  
        args = [left_file, right_file, output_file, "-automerge"]
    
    result = await run_bcompare_command(args)
    
    if result.success and os.path.exists(output_file):
        return f"Files merged successfully. Output saved to: {output_file}"
    else:
        return f"Merge failed: {result.error or 'Unknown error'}"


def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Beyond Compare MCP Server")
    
    # Check if Beyond Compare is available
    if not find_bcompare_executable():
        logger.error("Beyond Compare not found. Please install Beyond Compare.")
        sys.exit(1)
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

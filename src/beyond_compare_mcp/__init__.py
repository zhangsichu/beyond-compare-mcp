"""Beyond Compare MCP Server - Natural language interface for Beyond Compare operations."""

try:
    from .server import BeyondCompareError, BeyondCompareManager
except ImportError:
    # Handle case when running as standalone module
    from server import BeyondCompareError, BeyondCompareManager

__version__ = "1.0.0"
__author__ = "Beyond Compare MCP"
__description__ = "MCP server for Beyond Compare file and folder operations"

__all__ = [
    "BeyondCompareManager",
    "BeyondCompareError",
]

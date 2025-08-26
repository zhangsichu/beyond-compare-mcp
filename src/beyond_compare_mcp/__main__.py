#!/usr/bin/env python3
"""
Main entry point for Beyond Compare MCP Server
"""

import sys

try:
    from .server import mcp
except ImportError:
    # Handle case when running as standalone module
    from server import mcp


def main():
    """Main entry point"""
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

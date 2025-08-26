"""Configuration settings for Beyond Compare MCP Server"""

import os
from typing import Any


class BeyondCompareConfig:
    """Configuration class for Beyond Compare MCP Server"""

    def __init__(self):
        self.settings = self._load_default_settings()
        self._load_environment_settings()

    def _load_default_settings(self) -> dict[str, Any]:
        """Load default configuration settings"""
        return {
            "timeout": 30,  # Default timeout for BC operations
            "max_file_size": 100 * 1024 * 1024,  # 100MB max file size
            "supported_formats": [
                ".txt",
                ".log",
                ".ini",
                ".cfg",
                ".py",
                ".js",
                ".java",
                ".cpp",
                ".cs",
                ".html",
                ".css",
                ".xml",
                ".json",
                ".yaml",
                ".csv",
                ".md",
                ".rst",
                ".sql",
                ".sh",
                ".bat",
                ".ps1",
            ],
            "ignore_patterns": [
                "*.tmp",
                "*.temp",
                "*.bak",
                "*.swp",
                "*.DS_Store",
                "__pycache__",
                "node_modules",
                ".git",
                ".svn",
            ],
            "default_comparison_options": {
                "ignore_case": False,
                "ignore_whitespace": False,
                "ignore_line_endings": False,
            },
        }

    def _load_environment_settings(self):
        """Load settings from environment variables"""
        env_timeout = os.getenv("BC_MCP_TIMEOUT")
        if env_timeout:
            try:
                self.settings["timeout"] = int(env_timeout)
            except ValueError:
                pass

        env_max_size = os.getenv("BC_MCP_MAX_FILE_SIZE")
        if env_max_size:
            try:
                self.settings["max_file_size"] = int(env_max_size)
            except ValueError:
                pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.settings[key] = value

    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.settings["supported_formats"]

    def should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns"""
        import fnmatch

        filename = os.path.basename(file_path)
        for pattern in self.settings["ignore_patterns"]:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False


# Global configuration instance
config = BeyondCompareConfig()

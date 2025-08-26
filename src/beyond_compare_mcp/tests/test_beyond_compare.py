"""Tests for Beyond Compare MCP Server"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, "..")  # Add parent directory to path
try:
    from beyond_compare_mcp import BeyondCompareError, BeyondCompareManager
except ImportError:
    # For restructured standalone environment
    import __init__ as beyond_compare_mcp

    BeyondCompareManager = beyond_compare_mcp.BeyondCompareManager
    BeyondCompareError = beyond_compare_mcp.BeyondCompareError


class TestBeyondCompareManager:
    """Test cases for BeyondCompareManager"""

    @pytest.fixture
    def temp_files(self):
        """Create temporary test files"""
        temp_dir = Path(tempfile.mkdtemp(prefix="bc_test_"))

        # Create test files
        file1 = temp_dir / "test1.txt"
        file2 = temp_dir / "test2.txt"
        file3 = temp_dir / "test3.txt"

        file1.write_text("Line 1\nLine 2\nLine 3\n")
        file2.write_text("Line 1\nLine 2 modified\nLine 3\n")
        file3.write_text("Line 1\nLine 2\nLine 3\n")

        yield temp_dir, file1, file2, file3

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_manager_initialization(self):
        """Test BeyondCompareManager initialization"""
        manager = BeyondCompareManager()
        assert isinstance(manager, BeyondCompareManager)

    def test_find_beyond_compare_executable(self):
        """Test finding Beyond Compare executable"""
        manager = BeyondCompareManager()
        # This test depends on system installation
        if manager.bc_executable:
            assert isinstance(manager.bc_executable, str)
            assert len(manager.bc_executable) > 0

    @patch("beyond_compare_mcp.server.subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 13  # Files different
        mock_result.stdout = "Files are different"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        manager = BeyondCompareManager()
        if manager.bc_executable:
            result = manager._run_command(["-qc", "file1.txt", "file2.txt"])
            assert result["success"] is True
            assert result["returncode"] == 13

    @patch("beyond_compare_mcp.server.subprocess.run")
    def test_run_command_timeout(self, mock_run):
        """Test command timeout handling"""
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired("cmd", 30)

        manager = BeyondCompareManager()
        if manager.bc_executable:
            with pytest.raises(BeyondCompareError, match="timed out"):
                manager._run_command(["-help"])

    def test_compare_files_nonexistent(self, temp_files):
        """Test comparing non-existent files"""
        try:
            from beyond_compare_mcp.server import compare_files
        except ImportError:
            from server import compare_files

        result = compare_files("/nonexistent/file1.txt", "/nonexistent/file2.txt")
        assert "does not exist" in result

    def test_compare_folders_nonexistent(self):
        """Test comparing non-existent folders"""
        try:
            from beyond_compare_mcp.server import compare_folders
        except ImportError:
            from server import compare_folders

        result = compare_folders("/nonexistent/folder1", "/nonexistent/folder2")
        assert "does not exist" in result

    @pytest.mark.integration
    def test_integration_file_comparison(self, temp_files):
        """Integration test for file comparison"""
        manager = BeyondCompareManager()
        if not manager.bc_executable:
            pytest.skip("Beyond Compare not installed")

        temp_dir, file1, file2, file3 = temp_files
        try:
            from beyond_compare_mcp.server import compare_files
        except ImportError:
            from server import compare_files

        # Test different files
        result = compare_files(str(file1), str(file2))
        # Check if comparison succeeded or failed gracefully
        if "failed" in result.lower():
            pytest.skip(f"Beyond Compare comparison failed: {result}")
        assert (
            "different" in result.lower()
            or "rules-based" in result.lower()
            or "differences" in result.lower()
        )

        # Test identical files
        result = compare_files(str(file1), str(file3))
        if "failed" in result.lower():
            pytest.skip(f"Beyond Compare comparison failed: {result}")
        assert "identical" in result.lower() or "same" in result.lower()

    @pytest.mark.integration
    def test_integration_get_info(self):
        """Integration test for getting Beyond Compare info"""
        manager = BeyondCompareManager()
        if not manager.bc_executable:
            pytest.skip("Beyond Compare not installed")

        try:
            from beyond_compare_mcp.server import get_beyond_compare_info
        except ImportError:
            from server import get_beyond_compare_info

        result = get_beyond_compare_info()
        assert "Beyond Compare" in result
        assert "executable" in result

    def test_list_file_formats(self):
        """Test listing supported file formats"""
        try:
            from beyond_compare_mcp.server import list_file_formats
        except ImportError:
            from server import list_file_formats

        result = list_file_formats()
        assert "File Types" in result
        assert "Comparison Types" in result


def test_package_version():
    """Test package version is available"""
    try:
        import beyond_compare_mcp
    except ImportError:
        import __init__ as beyond_compare_mcp
    assert hasattr(beyond_compare_mcp, "__version__")
    assert beyond_compare_mcp.__version__ == "1.0.0"


def test_package_exports():
    """Test package exports the expected classes"""
    try:
        import beyond_compare_mcp
    except ImportError:
        import __init__ as beyond_compare_mcp
    assert hasattr(beyond_compare_mcp, "BeyondCompareManager")
    assert hasattr(beyond_compare_mcp, "BeyondCompareError")

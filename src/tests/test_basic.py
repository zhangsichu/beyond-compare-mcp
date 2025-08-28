#!/usr/bin/env python3
"""
Basic test to verify Beyond Compare MCP Server functionality
"""

import tempfile
import os
from pathlib import Path

# Test helper - create test files
def create_test_files():
    """Create temporary test files for comparison"""
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create test files
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.txt"
    file3 = temp_dir / "file3.txt"
    
    file1.write_text("Hello World\nThis is line 2\nCommon line\n")
    file2.write_text("Hello Universe\nThis is line 2\nCommon line\nExtra line\n")
    file3.write_text("Hello World\nThis is line 2\nCommon line\n")  # Identical to file1
    
    return temp_dir, str(file1), str(file2), str(file3)

def test_beyond_compare_available():
    """Test that Beyond Compare is available on the system"""
    from beyond_compare_mcp.server import find_bcompare_executable
    
    bcomp_path = find_bcompare_executable()
    if bcomp_path:
        print(f"✓ Beyond Compare found at: {bcomp_path}")
        return True
    else:
        print("✗ Beyond Compare not found")
        return False

def test_path_validation():
    """Test path validation functionality"""
    from beyond_compare_mcp.server import validate_path
    
    # Test existing path
    if validate_path("/"):
        print("✓ Path validation works for existing paths")
    else:
        print("✗ Path validation failed for existing paths")
        return False
    
    # Test non-existing path
    if not validate_path("/nonexistent/path/that/should/not/exist"):
        print("✓ Path validation correctly rejects non-existing paths")
        return True
    else:
        print("✗ Path validation incorrectly accepted non-existing path")
        return False

def main():
    """Run basic tests"""
    print("Running Beyond Compare MCP Server Basic Tests")
    print("=" * 50)
    
    # Test 1: Beyond Compare availability
    print("Test 1: Beyond Compare availability")
    bc_available = test_beyond_compare_available()
    print()
    
    # Test 2: Path validation
    print("Test 2: Path validation")
    path_validation_works = test_path_validation()
    print()
    
    # Test 3: Test file creation for manual testing
    print("Test 3: Creating test files for manual comparison")
    try:
        temp_dir, file1, file2, file3 = create_test_files()
        print(f"✓ Created test files in: {temp_dir}")
        print(f"  - file1.txt (original): {file1}")
        print(f"  - file2.txt (modified): {file2}")
        print(f"  - file3.txt (identical): {file3}")
        print("\nYou can manually test Beyond Compare with these files:")
        print(f"  bcomp '{file1}' '{file2}'")
        print(f"  bcomp '{file1}' '{file3}'")
    except Exception as e:
        print(f"✗ Failed to create test files: {e}")
        temp_dir = None
    print()
    
    # Summary
    print("Summary:")
    print("=" * 50)
    if bc_available:
        print("✓ Beyond Compare is available - MCP server should work")
    else:
        print("✗ Beyond Compare not found - please install Beyond Compare")
    
    if path_validation_works:
        print("✓ Path validation working correctly")
    else:
        print("✗ Path validation has issues")
    
    if temp_dir:
        print(f"✓ Test files created in: {temp_dir}")
        print("  (Remember to clean up when done testing)")
    
    print("\nTo test the MCP server:")
    print("1. Run: uv run beyond-compare-mcp")
    print("2. Configure in Cursor IDE (run: uv run python setup_cursor.py)")
    print("3. Try prompts like 'Compare these two files'")

if __name__ == "__main__":
    main()

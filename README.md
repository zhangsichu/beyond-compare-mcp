# Beyond Compare MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Model Context Protocol (MCP) server** that provides natural language interface to Beyond Compare operations. This server allows Large Language Models (LLMs) to perform file and folder comparisons, synchronization, and other Beyond Compare operations through simple natural language commands.

## 🚀 Features

- **🔗 MCP Protocol Support**: Seamless integration with any MCP-compliant LLM or agent
- **📁 File & Folder Operations**: Compare files, folders, and generate reports
- **🔄 Synchronization**: Sync folders with different strategies and preview modes
- **🌐 Multiple Interfaces**: MCP server + standalone HTTP server for testing
- **🛠️ Modern Architecture**: Built with UV package manager and modern Python practices
- **🧪 Well Tested**: Comprehensive test suite with 90%+ coverage

## 📋 Prerequisites

1. **Beyond Compare**: Install from [scootersoftware.com](https://www.scootersoftware.com/)
   - Ensure command-line tools are available (`bcomp` on macOS/Linux, `BCompare.exe` on Windows)

2. **Python 3.10+**: Required for MCP package compatibility

3. **UV Package Manager** (recommended): Install from [docs.astral.sh/uv](https://docs.astral.sh/uv/)

## 🛠️ Available MCP Tools

| Tool Name | Description |
|-----------|-------------|
| `compare_files` | Compare two files with various options (ignore case, whitespace, etc.) |
| `compare_folders` | Compare directory structures recursively |
| `sync_folders` | Synchronize folders with different strategies and preview mode |
| `generate_report` | Generate comparison reports in multiple formats (HTML, XML, CSV, text) |
| `get_beyond_compare_info` | Get information about Beyond Compare installation |
| `list_file_formats` | List supported file formats and comparison capabilities |

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/zhangsichu/beyond-compare-mcp.git
cd beyond-compare-mcp/src/beyond_compare_mcp
```

### 2. Install Dependencies

```bash
# Using UV (recommended)
uv sync
```

### 3. Run the Server

```bash
# Start standalone HTTP server (for testing and web interface)
uv run python standalone_server.py

# OR start MCP server (for IDE integration)
uv run python __main__.py
```

### 4. Test the Installation

```bash
# Run tests to verify everything works
uv run python -m pytest tests/ -v

# Quick functionality test
uv run python -c "
import sys; sys.path.insert(0, '.')
import __init__ as bc_mcp
manager = bc_mcp.BeyondCompareManager()
print(f'✅ Beyond Compare found: {manager.bc_executable}')
"
```

## 📖 Usage Examples

### With MCP-Compatible LLMs

Once the server is running, you can use natural language commands with any MCP-compatible LLM:

```
"Compare these two files: /path/to/file1.txt and /path/to/file2.txt"

"Sync the folder /source to /destination"

"Generate an HTML report comparing /folder1 and /folder2"

"What file formats does Beyond Compare support?"
```

### HTTP API (Testing)

When running the standalone server:

```bash
# Check server status
curl http://localhost:8000/status

# Compare files via REST API
curl -X POST http://localhost:8000/api/compare_files \
  -H "Content-Type: application/json" \
  -d '{"left_file": "/path/to/file1.txt", "right_file": "/path/to/file2.txt"}'

# Web interface
open http://localhost:8000
```

### Direct Python Usage

```python
import sys
sys.path.insert(0, 'src/beyond_compare_mcp')
import __init__ as beyond_compare_mcp

# Create manager
manager = beyond_compare_mcp.BeyondCompareManager()

# Compare files
from server import compare_files
result = compare_files("/path/to/file1.txt", "/path/to/file2.txt")
print(result)
```

## 🧩 IDE Integration

The Beyond Compare MCP server can be integrated with various IDEs and AI assistants that support the Model Context Protocol (MCP). Here's how to set it up:

### Claude Desktop (Anthropic)

1. **Install the MCP server** following the Quick Start guide above

2. **Configure Claude Desktop** by editing the MCP configuration file:

   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add the server configuration:**

```json
{
  "mcpServers": {
    "beyond-compare": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "__main__.py"
      ],
      "cwd": "/path/to/your/beyond-compare-mcp/src/beyond_compare_mcp"
    }
  }
}
```

4. **Restart Claude Desktop** and you'll see the Beyond Compare tools available

### Cursor IDE

1. **Ensure MCP support** is enabled in Cursor settings

2. **Add to Cursor's MCP configuration** (usually in `.cursor/mcp_config.json`):

```json
{
  "servers": {
    "beyond-compare": {
      "command": "uv",
      "args": ["run", "python", "__main__.py"],
      "cwd": "/path/to/your/beyond-compare-mcp/src/beyond_compare_mcp"
    }
  }
}
```

### VS Code with MCP Extension

1. **Install an MCP extension** that supports external servers

2. **Configure the extension** to point to your MCP server:

```json
{
  "mcp.servers": [
    {
      "name": "beyond-compare",
      "command": "uv run python __main__.py",
      "workingDirectory": "/path/to/your/beyond-compare-mcp/src/beyond_compare_mcp"
    }
  ]
}
```

### Generic MCP Client Integration

For any MCP-compatible client:

1. **Server Command:** `uv run python __main__.py`
2. **Working Directory:** `/path/to/your/beyond-compare-mcp/src/beyond_compare_mcp`
3. **Protocol:** JSON-RPC over stdio
4. **Server Name:** `BeyondCompare`

### Usage in IDE/AI Assistant

Once integrated, you can use natural language commands like:

**File Comparison:**
```
"Compare the current file with its previous version"
"Show me the differences between these two configuration files"
"Are there any changes in /project/src/ compared to /project/backup/src/?"
```

**Folder Synchronization:**
```
"Sync my local project folder with the backup folder"
"Preview what changes would be made if I sync these directories"
"Help me merge changes from the development folder to production"
```

**Report Generation:**
```
"Generate an HTML comparison report for these two folders"
"Create a detailed report showing all differences between these directories"
"Export comparison results to CSV format"
```

**System Information:**
```
"Check if Beyond Compare is properly installed"
"What file types can Beyond Compare handle?"
"Show me the Beyond Compare version and capabilities"
```

### Troubleshooting IDE Integration

**Common Issues:**

1. **"Command not found" errors:**
   - Ensure `uv` is in your system PATH
   - Use full path to `uv` executable if needed
   - Verify the working directory path is correct

2. **"Beyond Compare not found" errors:**
   - Install Beyond Compare from [scootersoftware.com](https://www.scootersoftware.com/)
   - Ensure command-line tools are installed
   - Check that `bcomp` (macOS/Linux) or `BCompare.exe` (Windows) is accessible

3. **Permission errors:**
   - Ensure the user has read/write access to the directories being compared
   - On macOS, you might need to grant file access permissions to your IDE

4. **MCP connection issues:**
   - Verify the server starts correctly: `uv run python __main__.py`
   - Check that JSON-RPC messages are properly formatted
   - Look for error messages in the IDE's MCP logs

**Testing the Integration:**

```bash
# Test that the server responds to MCP initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' | uv run python __main__.py
```

**Example IDE Commands:**

Once integrated, your AI assistant can help with tasks like:
- "Compare the files I have open and tell me what changed"
- "Sync my project directory with the backup and show me a preview"
- "Generate a report of all differences in this codebase"
- "Help me identify which files are different between these two versions"

## 🔧 Development

### Project Structure

```
beyond-compare-mcp/
├── 📄 README.md              # This file
├── 📄 LICENSE                # MIT license
├── 📄 .gitignore             # Git ignore rules
└── 📁 src/beyond_compare_mcp/    # Main implementation
    ├── 📄 __init__.py        # Package initialization
    ├── 📄 __main__.py        # MCP server entry point
    ├── 📄 server.py          # Core MCP server logic
    ├── 📄 standalone_server.py # HTTP server for testing
    ├── 📄 config.py          # Configuration management
    ├── 📄 utils.py           # Utility functions
    ├── 📄 pyproject.toml     # Project configuration
    ├── 📄 uv.lock            # Dependency lock file
    ├── 📁 .venv/             # Virtual environment
    └── 📁 tests/             # Test suite
        └── test_beyond_compare.py
```

### Development Commands

```bash
cd src/beyond_compare_mcp

# Install development dependencies
uv sync

# Run tests
uv run python -m pytest tests/ -v

# Run tests without integration tests
uv run python -m pytest tests/ -v -m "not integration"

# Code quality checks
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy .

# Start development server (HTTP server for testing)
uv run python standalone_server.py
```

### Adding New Tools

1. Add your tool function to `server.py`
2. Register it with the MCP server using `@mcp.tool()`
3. Add tests in `tests/test_beyond_compare.py`
4. Update this README's tools table

Example:
```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 5) -> str:
    """
    Description of what this tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 with default value
        
    Returns:
        Description of return value
    """
    # Implementation here
    return "result"
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ --cov=. --cov-report=html

# Run only fast tests (skip integration tests)
uv run python -m pytest tests/ -v -m "not integration"
```

## 🔧 Configuration

The server can be configured via environment variables or the `config.py` file:

- `BC_EXECUTABLE`: Path to Beyond Compare executable (auto-detected)
- `BC_TIMEOUT`: Command timeout in seconds (default: 30)
- `HTTP_PORT`: Port for standalone HTTP server (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## 🚀 Deployment

### As MCP Server

1. Install the package in your MCP environment
2. Configure your MCP client to use this server
3. Start the server with `python __main__.py`

### As Standalone Service

1. Run `python standalone_server.py`
2. The HTTP server will start on port 8000
3. Access the web interface or use the REST API

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY src/beyond_compare_mcp/ .

RUN pip install uv
RUN uv sync --no-dev

EXPOSE 8000
CMD ["uv", "run", "python", "standalone_server.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes in `src/beyond_compare_mcp/`
4. Add tests for new functionality
5. Run the test suite: `uv run python -m pytest tests/ -v`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Beyond Compare](https://www.scootersoftware.com/) for the excellent file comparison tool
- [Model Context Protocol](https://modelcontextprotocol.io/) for the standardized interface
- [UV](https://docs.astral.sh/uv/) for modern Python package management

## 📚 Related Projects

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Beyond Compare Documentation](https://www.scootersoftware.com/v5help/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

---

**Made with ❤️ for the MCP ecosystem**
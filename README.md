# Beyond Compare MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Model Context Protocol (MCP) server** that provides natural language interface to Beyond Compare operations. This server allows Large Language Models (LLMs) to perform file and folder comparisons, synchronization, and other Beyond Compare operations through simple natural language commands.

## Features

🔍 **File Comparison**
- Compare two files with detailed difference analysis
- Support for text and HTML output formats
- Automatic detection of identical vs different files

📁 **Folder Comparison** 
- Compare entire directory structures
- Optional recursive subdirectory comparison
- Comprehensive difference reporting

📊 **Report Generation**
- Generate detailed comparison reports in HTML, XML, or text formats
- Customizable report paths and formats
- Professional-quality comparison documentation

🔄 **Folder Synchronization**
- Mirror synchronization (make target identical to source)
- Update synchronization (copy only newer files)
- Safe directory creation and validation

🔀 **File Merging**
- 2-way file merging
- 3-way merging with base file support
- Automatic merge conflict resolution

## Prerequisites

- **Beyond Compare**: This server requires Beyond Compare to be installed on your system
  - macOS: [Download Beyond Compare for Mac](https://www.scootersoftware.com/download.php)
  - Windows: [Download Beyond Compare for Windows](https://www.scootersoftware.com/download.php)
  - Linux: [Download Beyond Compare for Linux](https://www.scootersoftware.com/download.php)

- **Python 3.13+**: Required for the MCP server

## Installation

1. **Clone and set up the project:**
   ```bash
   git clone git@github.com:zhangsichu/beyond-compare-mcp.git
   cd beyond-compare-mcp
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Verify Beyond Compare installation:**
   ```bash
   # Test that Beyond Compare is accessible
   bcomp --help
   ```

## Usage with Cursor IDE

This MCP server integrates seamlessly with Cursor IDE, enabling you to use Beyond Compare's powerful comparison tools through natural language commands.

### Quick Setup
1. Open Cursor Settings (`Cmd + ,` or `Ctrl + ,`)
2. Search for "MCP" or "Model Context Protocol"
3. Add a new MCP server:
   - **Name:** `beyond-compare`
   - **Command:** `uv`
   - **Args:** `--directory /{your-source-folder} run beyond-compare-mcp`
4. Restart Cursor IDE
5. Start comparing files with natural language prompts!

```json
{
  "mcpServers": {
    "beyond-compare": {
      "command": "uv",
      "args": [
        "--directory",
        "/{your-source-folder}",
        "run",
        "beyond-compare-mcp"
      ],
      "description": "Beyond Compare file and folder comparison tools"
    }
  }
}
```

## Available Tools

### 1. `compare_files`
Compare two files and identify differences.

**Parameters:**
- `left_file` (str): Path to the first file
- `right_file` (str): Path to the second file  
- `output_format` (str, optional): "text" or "html" (default: "text")

**Example:**
```
Compare /path/to/file1.txt with /path/to/file2.txt in HTML format
```

### 2. `compare_folders`
Compare two directories and their contents.

**Parameters:**
- `left_folder` (str): Path to the first folder
- `right_folder` (str): Path to the second folder
- `include_subdirs` (bool, optional): Include subdirectories (default: true)

**Example:**
```
Compare the folders /project/v1 and /project/v2 including all subdirectories
```

### 3. `generate_comparison_report`
Generate a detailed comparison report in various formats.

**Parameters:**
- `left_path` (str): Path to first file/folder
- `right_path` (str): Path to second file/folder
- `report_path` (str): Where to save the report
- `report_format` (str, optional): "html", "xml", or "text" (default: "html")

**Example:**
```
Generate an HTML comparison report for /src/old and /src/new, save it to /reports/comparison.html
```

### 4. `sync_folders`
Synchronize two folders using different strategies.

**Parameters:**
- `source_folder` (str): Source directory path
- `target_folder` (str): Target directory path
- `sync_mode` (str, optional): "mirror" or "update" (default: "mirror")

**Example:**
```
Mirror sync /backup/source to /backup/target
```

### 5. `merge_files`
Merge two or three files with conflict resolution.

**Parameters:**
- `left_file` (str): Path to left file
- `right_file` (str): Path to right file
- `output_file` (str): Path for merged output
- `base_file` (str, optional): Base file for 3-way merge

**Example:**
```
Merge /branch1/config.json and /branch2/config.json, save result to /merged/config.json
```

## Example Conversations in Cursor IDE

Here are some example prompts you can use:

1. **"Compare these two configuration files and show me the differences in HTML format"**
   - Uses `compare_files` with HTML output

2. **"Check if these two project directories are in sync"**  
   - Uses `compare_folders` to analyze directory differences

3. **"Generate a detailed comparison report between the old and new versions of my code"**
   - Uses `generate_comparison_report` to create comprehensive documentation

4. **"Sync my backup folder with the latest changes, but only copy newer files"**
   - Uses `sync_folders` with "update" mode

5. **"Merge these conflicting configuration files from two git branches"**
   - Uses `merge_files` to resolve conflicts

## Development

### Running the server standalone

```bash
# Run with uv
uv run beyond-compare-mcp

# Or activate the virtual environment and run directly
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
python -m beyond_compare_mcp.server
```

### Testing

You can test individual tools by running the server and sending MCP requests, or use the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector uv run beyond-compare-mcp
```

```bash
uv run python src/tests/test_basic.py
```
## Troubleshooting

### Common Issues

1. **"Beyond Compare executable not found"**
   - Ensure Beyond Compare is installed and accessible in your PATH
   - On macOS, the installer usually places it at `/Applications/Beyond Compare.app/Contents/MacOS/bcomp`

2. **"Permission denied" errors**
   - Check file/folder permissions for the paths you're comparing
   - Ensure the target directories for reports/sync operations are writable

3. **Server not appearing in Cursor IDE**
   - Verify the MCP configuration in Cursor settings
   - Check that the absolute path to the project is correct
   - Restart Cursor IDE after configuration changes

4. **MCP connection issues**
   - Check Cursor's MCP logs (location varies by platform)
   - Ensure all dependencies are installed with `uv sync`
   - Try running the setup helper: `uv run python setup_cursor.py`

### Debug Logging

The server logs to stderr. Check Cursor's logs or run the server manually to see debug output:

```bash
uv run beyond-compare-mcp
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Related Links

- [Beyond Compare Official Documentation](https://www.scootersoftware.com/v5help/)
- [Beyond Compare Command Line Reference](https://www.scootersoftware.com/v5help/command_line_reference.html)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Cursor IDE Documentation](https://docs.cursor.com/)

#!/usr/bin/env python3
"""
Standalone Beyond Compare Server (Python 3.8+ compatible)

This is a lightweight HTTP server that provides Beyond Compare functionality
without requiring the full MCP package. Useful for older Python versions.
"""

import json
import logging
import os
import shutil
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class BeyondCompareHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Beyond Compare operations"""

    def do_POST(self):
        """Handle POST requests"""
        try:
            # Parse request
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode("utf-8"))

            # Get operation and parameters
            operation = request_data.get("operation")
            params = request_data.get("params", {})

            # Execute operation
            if operation == "compare_files":
                result = self.compare_files(**params)
            elif operation == "compare_folders":
                result = self.compare_folders(**params)
            elif operation == "sync_folders":
                result = self.sync_folders(**params)
            elif operation == "generate_report":
                result = self.generate_report(**params)
            elif operation == "get_info":
                result = self.get_beyond_compare_info()
            elif operation == "list_formats":
                result = self.list_file_formats()
            else:
                result = {"error": f"Unknown operation: {operation}"}

            # Send response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = self.get_web_interface()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            status = {
                "status": "running",
                "beyond_compare_found": bc_manager.bc_executable is not None,
                "executable": bc_manager.bc_executable,
            }
            self.wfile.write(json.dumps(status).encode("utf-8"))
        else:
            self.send_error(404, "Not found")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def compare_files(
        self, left_file: str, right_file: str, **kwargs
    ) -> dict[str, Any]:
        """Compare two files"""
        try:
            if not os.path.exists(left_file):
                return {"error": f"Left file '{left_file}' does not exist"}
            if not os.path.exists(right_file):
                return {"error": f"Right file '{right_file}' does not exist"}

            args = ["-qc", left_file, right_file]
            result = bc_manager._run_command(args)

            if result["returncode"] < 100:  # Success codes are < 100
                if result["returncode"] == 0:
                    return {"result": "Files are identical (Success)"}
                elif result["returncode"] == 1:
                    return {"result": "Files are binary identical"}
                elif result["returncode"] == 2:
                    return {"result": "Files are rules-based identical"}
                elif result["returncode"] == 11:
                    return {"result": "Files have binary differences"}
                elif result["returncode"] == 12:
                    return {"result": "Files are similar"}
                elif result["returncode"] == 13:
                    return {"result": "Files have rules-based differences"}
                elif result["returncode"] == 14:
                    return {"result": "Conflicts detected in files"}
                else:
                    return {
                        "result": f"Files compared (return code: {result['returncode']})"
                    }
            else:
                return {
                    "error": f"Comparison failed with error code {result['returncode']}: {result['stderr']}"
                }

        except Exception as e:
            return {"error": f"Error comparing files: {str(e)}"}

    def compare_folders(
        self, left_folder: str, right_folder: str, **kwargs
    ) -> dict[str, Any]:
        """Compare two folders"""
        try:
            if not os.path.exists(left_folder):
                return {"error": f"Left folder '{left_folder}' does not exist"}
            if not os.path.exists(right_folder):
                return {"error": f"Right folder '{right_folder}' does not exist"}

            args = ["-qc", left_folder, right_folder]
            result = bc_manager._run_command(args)

            if result["success"]:
                output = (
                    result["stdout"]
                    if result["stdout"]
                    else "Folders compared successfully"
                )
                return {"result": f"Folder comparison result:\n{output}"}
            else:
                return {"error": f"Folder comparison failed: {result['stderr']}"}

        except Exception as e:
            return {"error": f"Error comparing folders: {str(e)}"}

    def sync_folders(
        self, source_folder: str, target_folder: str, **kwargs
    ) -> dict[str, Any]:
        """Synchronize two folders"""
        try:
            if not os.path.exists(source_folder):
                return {"error": f"Source folder '{source_folder}' does not exist"}
            if not os.path.exists(target_folder):
                return {"error": f"Target folder '{target_folder}' does not exist"}

            args = ["-sync", source_folder, target_folder]
            result = bc_manager._run_command(args)

            if result["success"]:
                output = (
                    result["stdout"]
                    if result["stdout"]
                    else "Preview of synchronization completed"
                )
                return {"result": f"Synchronization preview:\n{output}"}
            else:
                return {"error": f"Synchronization failed: {result['stderr']}"}

        except Exception as e:
            return {"error": f"Error synchronizing folders: {str(e)}"}

    def generate_report(
        self, left_path: str, right_path: str, **kwargs
    ) -> dict[str, Any]:
        """Generate a comparison report"""
        try:
            if not os.path.exists(left_path):
                return {"error": f"Left path '{left_path}' does not exist"}
            if not os.path.exists(right_path):
                return {"error": f"Right path '{right_path}' does not exist"}

            output_file = kwargs.get("output_file", "bc_report.html")
            report_type = kwargs.get("report_type", "html")

            args = [
                "-silent",
                "-report",
                report_type,
                "-reportfile",
                output_file,
                left_path,
                right_path,
            ]
            result = bc_manager._run_command(args)

            if result["success"]:
                return {"result": f"Report generated successfully: {output_file}"}
            else:
                return {"error": f"Report generation failed: {result['stderr']}"}

        except Exception as e:
            return {"error": f"Error generating report: {str(e)}"}

    def get_beyond_compare_info(self) -> dict[str, Any]:
        """Get Beyond Compare information"""
        try:
            if not bc_manager.bc_executable:
                return {
                    "result": "Beyond Compare is not installed or not found in PATH"
                }

            result = bc_manager._run_command(["-help"])
            info = f"Beyond Compare executable: {bc_manager.bc_executable}\n"

            if result["success"]:
                info += f"Version information:\n{result['stdout'][:500]}..."
            else:
                info += "Could not retrieve version information"

            return {"result": info}

        except Exception as e:
            return {"error": f"Error getting Beyond Compare info: {str(e)}"}

    def list_file_formats(self) -> dict[str, Any]:
        """List supported file formats"""
        formats_info = """
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
"""
        return {"result": formats_info}

    def get_web_interface(self) -> str:
        """Get HTML web interface"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Beyond Compare MCP Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .operation { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        input, textarea, select { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #005a87; }
        .result { margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 3px; white-space: pre-wrap; }
        .error { background: #ffe6e6; color: #d00; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Beyond Compare MCP Server</h1>
        <p>Web interface for testing Beyond Compare operations</p>
        
        <div class="operation">
            <h3>Compare Files</h3>
            <input type="text" id="file1" placeholder="Path to first file">
            <input type="text" id="file2" placeholder="Path to second file">
            <button onclick="compareFiles()">Compare Files</button>
            <div id="fileResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="operation">
            <h3>Compare Folders</h3>
            <input type="text" id="folder1" placeholder="Path to first folder">
            <input type="text" id="folder2" placeholder="Path to second folder">
            <button onclick="compareFolders()">Compare Folders</button>
            <div id="folderResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="operation">
            <h3>Server Status</h3>
            <button onclick="getStatus()">Check Status</button>
            <div id="statusResult" class="result" style="display:none;"></div>
        </div>
    </div>
    
    <script>
        async function makeRequest(operation, params) {
            try {
                const response = await fetch('/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ operation, params })
                });
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        }
        
        async function compareFiles() {
            const file1 = document.getElementById('file1').value;
            const file2 = document.getElementById('file2').value;
            const result = await makeRequest('compare_files', { left_file: file1, right_file: file2 });
            showResult('fileResult', result);
        }
        
        async function compareFolders() {
            const folder1 = document.getElementById('folder1').value;
            const folder2 = document.getElementById('folder2').value;
            const result = await makeRequest('compare_folders', { left_folder: folder1, right_folder: folder2 });
            showResult('folderResult', result);
        }
        
        async function getStatus() {
            try {
                const response = await fetch('/status');
                const result = await response.json();
                showResult('statusResult', result);
            } catch (error) {
                showResult('statusResult', { error: error.message });
            }
        }
        
        function showResult(elementId, result) {
            const element = document.getElementById(elementId);
            element.style.display = 'block';
            element.className = 'result ' + (result.error ? 'error' : '');
            element.textContent = JSON.stringify(result, null, 2);
        }
    </script>
</body>
</html>
"""


def main():
    """Main function to start the server"""
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting Beyond Compare Standalone Server on port {port}")
    print(f"Beyond Compare executable: {bc_manager.bc_executable}")
    print(f"Web interface: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")

    server = HTTPServer(("localhost", port), BeyondCompareHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        server.shutdown()


if __name__ == "__main__":
    main()

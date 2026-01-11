"""LSP (Language Server Protocol) tool for code intelligence."""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from app.tools.base import BaseTool


class LSPTool(BaseTool):
    """Tool for Language Server Protocol operations."""

    name = "lsp"
    description = "Code intelligence using LSP (go to definition, find references, hover, diagnostics)"

    def __init__(self):
        self.language_servers: Dict[str, Any] = {}

    async def execute(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute an LSP operation."""
        commands = {
            "goto_definition": self.goto_definition,
            "goto_references": self.find_references,
            "hover_symbol": self.hover_symbol,
            "file_diagnostics": self.get_diagnostics,
            "document_symbols": self.get_document_symbols,
            "workspace_symbols": self.search_workspace_symbols,
            "completion": self.get_completions,
            "signature_help": self.get_signature_help,
            "rename": self.rename_symbol,
            "format_document": self.format_document,
        }

        if command not in commands:
            return {"error": f"Unknown command: {command}"}

        return await commands[command](**kwargs)

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".cs": "csharp",
        }
        return language_map.get(ext, "unknown")

    def _parse_file_for_symbols(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Parse file content to extract symbols (basic implementation)."""
        symbols = []
        lines = content.split("\n")
        language = self._detect_language(file_path)

        for line_num, line in enumerate(lines, 1):
            # Python patterns
            if language == "python":
                # Class definitions
                class_match = re.match(r"^class\s+(\w+)", line)
                if class_match:
                    symbols.append({
                        "name": class_match.group(1),
                        "kind": "class",
                        "line": line_num,
                        "column": line.index("class") + 1,
                    })

                # Function definitions
                func_match = re.match(r"^\s*(?:async\s+)?def\s+(\w+)", line)
                if func_match:
                    symbols.append({
                        "name": func_match.group(1),
                        "kind": "function",
                        "line": line_num,
                        "column": line.index("def") + 1,
                    })

                # Variable assignments at module level
                var_match = re.match(r"^(\w+)\s*=", line)
                if var_match and not line.strip().startswith("#"):
                    symbols.append({
                        "name": var_match.group(1),
                        "kind": "variable",
                        "line": line_num,
                        "column": 1,
                    })

            # JavaScript/TypeScript patterns
            elif language in ["javascript", "typescript"]:
                # Function declarations
                func_match = re.match(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)", line)
                if func_match:
                    symbols.append({
                        "name": func_match.group(1),
                        "kind": "function",
                        "line": line_num,
                        "column": 1,
                    })

                # Class declarations
                class_match = re.match(r"^\s*(?:export\s+)?class\s+(\w+)", line)
                if class_match:
                    symbols.append({
                        "name": class_match.group(1),
                        "kind": "class",
                        "line": line_num,
                        "column": 1,
                    })

                # Const/let/var declarations
                var_match = re.match(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)", line)
                if var_match:
                    symbols.append({
                        "name": var_match.group(1),
                        "kind": "variable",
                        "line": line_num,
                        "column": 1,
                    })

                # Interface declarations (TypeScript)
                interface_match = re.match(r"^\s*(?:export\s+)?interface\s+(\w+)", line)
                if interface_match:
                    symbols.append({
                        "name": interface_match.group(1),
                        "kind": "interface",
                        "line": line_num,
                        "column": 1,
                    })

                # Type declarations (TypeScript)
                type_match = re.match(r"^\s*(?:export\s+)?type\s+(\w+)", line)
                if type_match:
                    symbols.append({
                        "name": type_match.group(1),
                        "kind": "type",
                        "line": line_num,
                        "column": 1,
                    })

            # Go patterns
            elif language == "go":
                # Function declarations
                func_match = re.match(r"^func\s+(?:\([^)]+\)\s+)?(\w+)", line)
                if func_match:
                    symbols.append({
                        "name": func_match.group(1),
                        "kind": "function",
                        "line": line_num,
                        "column": 1,
                    })

                # Type declarations
                type_match = re.match(r"^type\s+(\w+)", line)
                if type_match:
                    symbols.append({
                        "name": type_match.group(1),
                        "kind": "type",
                        "line": line_num,
                        "column": 1,
                    })

        return symbols

    async def goto_definition(
        self,
        path: str,
        symbol: str,
        line: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Find where a symbol is defined."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Search for definition in the same file
            symbols = self._parse_file_for_symbols(path, content)
            for sym in symbols:
                if sym["name"] == symbol:
                    return {
                        "success": True,
                        "definition": {
                            "path": path,
                            "line": sym["line"],
                            "column": sym["column"],
                            "kind": sym["kind"],
                        },
                    }

            # Search in directory for imports/definitions
            directory = os.path.dirname(path)
            for root, dirs, files in os.walk(directory):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "__pycache__", "venv", ".venv"]]

                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path == path:
                        continue

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()

                        file_symbols = self._parse_file_for_symbols(file_path, file_content)
                        for sym in file_symbols:
                            if sym["name"] == symbol:
                                return {
                                    "success": True,
                                    "definition": {
                                        "path": file_path,
                                        "line": sym["line"],
                                        "column": sym["column"],
                                        "kind": sym["kind"],
                                    },
                                }
                    except (UnicodeDecodeError, PermissionError):
                        continue

            return {
                "success": False,
                "message": f"Definition not found for symbol: {symbol}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def find_references(
        self,
        path: str,
        symbol: str,
        line: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Find all references to a symbol."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            references = []
            directory = os.path.dirname(path)

            # Search for references in all files
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "__pycache__", "venv", ".venv"]]

                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()

                        for line_num, line_content in enumerate(lines, 1):
                            # Simple word boundary search
                            pattern = rf"\b{re.escape(symbol)}\b"
                            for match in re.finditer(pattern, line_content):
                                references.append({
                                    "path": file_path,
                                    "line": line_num,
                                    "column": match.start() + 1,
                                    "context": line_content.strip(),
                                })
                    except (UnicodeDecodeError, PermissionError):
                        continue

            return {
                "success": True,
                "symbol": symbol,
                "references": references[:100],  # Limit to 100 references
                "total_count": len(references),
            }
        except Exception as e:
            return {"error": str(e)}

    async def hover_symbol(
        self,
        path: str,
        symbol: str,
        line: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get documentation/type info for a symbol."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            language = self._detect_language(path)

            # Find the symbol definition and extract docstring/comments
            symbols = self._parse_file_for_symbols(path, content)
            for sym in symbols:
                if sym["name"] == symbol:
                    # Get surrounding context
                    start_line = max(0, sym["line"] - 2)
                    end_line = min(len(lines), sym["line"] + 5)
                    context = "\n".join(lines[start_line:end_line])

                    # Extract docstring if Python
                    docstring = None
                    if language == "python" and sym["line"] < len(lines):
                        next_lines = lines[sym["line"]:sym["line"] + 10]
                        for i, line_text in enumerate(next_lines):
                            if '"""' in line_text or "'''" in line_text:
                                doc_start = i
                                quote = '"""' if '"""' in line_text else "'''"
                                for j, doc_line in enumerate(next_lines[i:], i):
                                    if j > i and quote in doc_line:
                                        docstring = "\n".join(next_lines[doc_start:j + 1])
                                        break
                                break

                    return {
                        "success": True,
                        "symbol": symbol,
                        "kind": sym["kind"],
                        "location": {
                            "path": path,
                            "line": sym["line"],
                            "column": sym["column"],
                        },
                        "context": context,
                        "docstring": docstring,
                    }

            return {
                "success": False,
                "message": f"Symbol not found: {symbol}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_diagnostics(
        self,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get errors/warnings for a file."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            language = self._detect_language(path)
            diagnostics = []

            # Run language-specific linters
            if language == "python":
                # Try running ruff or flake8
                try:
                    process = await asyncio.create_subprocess_exec(
                        "ruff", "check", "--output-format=json", path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, _ = await process.communicate()
                    if stdout:
                        results = json.loads(stdout.decode())
                        for item in results:
                            diagnostics.append({
                                "line": item.get("location", {}).get("row", 0),
                                "column": item.get("location", {}).get("column", 0),
                                "severity": "error" if item.get("code", "").startswith("E") else "warning",
                                "message": item.get("message", ""),
                                "code": item.get("code", ""),
                            })
                except FileNotFoundError:
                    pass

            elif language in ["javascript", "typescript"]:
                # Try running eslint
                try:
                    process = await asyncio.create_subprocess_exec(
                        "npx", "eslint", "--format=json", path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, _ = await process.communicate()
                    if stdout:
                        results = json.loads(stdout.decode())
                        for file_result in results:
                            for msg in file_result.get("messages", []):
                                diagnostics.append({
                                    "line": msg.get("line", 0),
                                    "column": msg.get("column", 0),
                                    "severity": "error" if msg.get("severity") == 2 else "warning",
                                    "message": msg.get("message", ""),
                                    "code": msg.get("ruleId", ""),
                                })
                except FileNotFoundError:
                    pass

            return {
                "success": True,
                "path": path,
                "language": language,
                "diagnostics": diagnostics,
                "count": len(diagnostics),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_document_symbols(
        self,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get all symbols in a document."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            symbols = self._parse_file_for_symbols(path, content)

            return {
                "success": True,
                "path": path,
                "symbols": symbols,
                "count": len(symbols),
            }
        except Exception as e:
            return {"error": str(e)}

    async def search_workspace_symbols(
        self,
        query: str,
        workspace_path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Search for symbols across the workspace."""
        try:
            if not os.path.exists(workspace_path):
                return {"error": f"Workspace not found: {workspace_path}"}

            matching_symbols = []

            for root, dirs, files in os.walk(workspace_path):
                dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "__pycache__", "venv", ".venv"]]

                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        symbols = self._parse_file_for_symbols(file_path, content)
                        for sym in symbols:
                            if query.lower() in sym["name"].lower():
                                sym["path"] = file_path
                                matching_symbols.append(sym)
                    except (UnicodeDecodeError, PermissionError):
                        continue

            return {
                "success": True,
                "query": query,
                "symbols": matching_symbols[:100],
                "total_count": len(matching_symbols),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_completions(
        self,
        path: str,
        line: int,
        column: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get code completions at a position."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Get symbols from current file for basic completions
            symbols = self._parse_file_for_symbols(path, content)
            completions = [
                {
                    "label": sym["name"],
                    "kind": sym["kind"],
                    "detail": f"{sym['kind']} defined at line {sym['line']}",
                }
                for sym in symbols
            ]

            return {
                "success": True,
                "completions": completions,
                "count": len(completions),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_signature_help(
        self,
        path: str,
        line: int,
        column: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get function signature help."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if line > len(lines):
                return {"error": f"Line {line} out of range"}

            current_line = lines[line - 1]

            # Find function call
            func_match = re.search(r"(\w+)\s*\(", current_line[:column])
            if not func_match:
                return {
                    "success": False,
                    "message": "No function call found at position",
                }

            func_name = func_match.group(1)

            return {
                "success": True,
                "function": func_name,
                "message": f"Signature help for {func_name} (basic implementation)",
            }
        except Exception as e:
            return {"error": str(e)}

    async def rename_symbol(
        self,
        path: str,
        symbol: str,
        new_name: str,
        line: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Rename a symbol across files."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            # Find all references first
            refs_result = await self.find_references(path, symbol, line)
            if "error" in refs_result:
                return refs_result

            references = refs_result.get("references", [])

            # Group by file
            files_to_update: Dict[str, List[Dict[str, Any]]] = {}
            for ref in references:
                file_path = ref["path"]
                if file_path not in files_to_update:
                    files_to_update[file_path] = []
                files_to_update[file_path].append(ref)

            # Preview changes
            return {
                "success": True,
                "symbol": symbol,
                "new_name": new_name,
                "files_affected": len(files_to_update),
                "total_occurrences": len(references),
                "preview": {
                    path: len(refs) for path, refs in files_to_update.items()
                },
                "message": "Use edit_file tool to apply the rename",
            }
        except Exception as e:
            return {"error": str(e)}

    async def format_document(
        self,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Format a document."""
        try:
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}

            language = self._detect_language(path)

            if language == "python":
                # Try black
                process = await asyncio.create_subprocess_exec(
                    "black", path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await process.communicate()

                if process.returncode == 0:
                    return {
                        "success": True,
                        "path": path,
                        "formatter": "black",
                    }
                else:
                    return {"error": f"Formatting failed: {stderr.decode()}"}

            elif language in ["javascript", "typescript"]:
                # Try prettier
                process = await asyncio.create_subprocess_exec(
                    "npx", "prettier", "--write", path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await process.communicate()

                if process.returncode == 0:
                    return {
                        "success": True,
                        "path": path,
                        "formatter": "prettier",
                    }
                else:
                    return {"error": f"Formatting failed: {stderr.decode()}"}

            return {
                "success": False,
                "message": f"No formatter available for language: {language}",
            }
        except FileNotFoundError as e:
            return {"error": f"Formatter not found: {e}"}
        except Exception as e:
            return {"error": str(e)}

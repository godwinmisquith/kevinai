"""Search tools (grep, glob)."""

import asyncio
import fnmatch
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.tools.base import BaseTool


class SearchTool(BaseTool):
    """Tool for searching files and content."""

    name = "search"
    description = "Search for files and content using glob and grep"

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a search operation."""
        if operation == "glob":
            return await self.glob_search(**kwargs)
        elif operation == "grep":
            return await self.grep_search(**kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}

    async def glob_search(
        self, pattern: str, path: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Find files matching a glob pattern."""
        try:
            base_path = Path(path)

            if not base_path.exists():
                return {"error": f"Path not found: {path}"}

            matches: List[str] = []

            # Handle patterns without **
            if "**" not in pattern:
                # Search anywhere in the path
                for root, dirs, files in os.walk(base_path):
                    for name in files + dirs:
                        if fnmatch.fnmatch(name, pattern):
                            matches.append(os.path.join(root, name))
            else:
                # Use pathlib glob for ** patterns
                for match in base_path.glob(pattern):
                    matches.append(str(match))

            # Sort and limit results
            matches = sorted(matches)[:1000]

            return {
                "pattern": pattern,
                "path": path,
                "matches": matches,
                "count": len(matches),
            }
        except Exception as e:
            return {"error": str(e)}

    async def grep_search(
        self,
        pattern: str,
        path: str,
        glob_pattern: Optional[str] = None,
        case_insensitive: bool = False,
        output_mode: str = "files_with_matches",
        context_before: int = 0,
        context_after: int = 0,
        head_limit: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Search for a pattern in files using ripgrep."""
        try:
            # Build ripgrep command
            cmd = ["rg"]

            if case_insensitive:
                cmd.append("-i")

            if output_mode == "files_with_matches":
                cmd.append("-l")
            elif output_mode == "count":
                cmd.append("-c")
            else:
                cmd.append("-n")  # Show line numbers for content mode
                if context_before > 0:
                    cmd.extend(["-B", str(context_before)])
                if context_after > 0:
                    cmd.extend(["-A", str(context_after)])

            if glob_pattern:
                cmd.extend(["--glob", glob_pattern])

            cmd.append(pattern)
            cmd.append(path)

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode("utf-8", errors="replace")

            # Apply head limit
            if head_limit:
                lines = output.split("\n")
                output = "\n".join(lines[:head_limit])

            return {
                "pattern": pattern,
                "path": path,
                "output": output,
                "return_code": process.returncode,
            }
        except FileNotFoundError:
            # Fallback to Python-based grep if ripgrep not available
            return await self._python_grep(
                pattern, path, glob_pattern, case_insensitive, output_mode
            )
        except Exception as e:
            return {"error": str(e)}

    async def _python_grep(
        self,
        pattern: str,
        path: str,
        glob_pattern: Optional[str],
        case_insensitive: bool,
        output_mode: str,
    ) -> Dict[str, Any]:
        """Fallback Python-based grep implementation."""
        try:
            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(pattern, flags)

            base_path = Path(path)
            results: List[str] = []

            if base_path.is_file():
                files = [base_path]
            else:
                if glob_pattern:
                    files = list(base_path.glob(glob_pattern))
                else:
                    files = [f for f in base_path.rglob("*") if f.is_file()]

            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if regex.search(content):
                            if output_mode == "files_with_matches":
                                results.append(str(file_path))
                            elif output_mode == "count":
                                count = len(regex.findall(content))
                                results.append(f"{file_path}:{count}")
                            else:
                                for i, line in enumerate(content.split("\n"), 1):
                                    if regex.search(line):
                                        results.append(f"{file_path}:{i}:{line}")
                except (UnicodeDecodeError, PermissionError):
                    continue

            return {
                "pattern": pattern,
                "path": path,
                "output": "\n".join(results),
                "return_code": 0 if results else 1,
            }
        except Exception as e:
            return {"error": str(e)}

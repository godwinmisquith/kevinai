"""File operations tool."""

import aiofiles
from typing import Any, Dict, Optional, List
from pathlib import Path
from app.tools.base import BaseTool


class FileOpsTool(BaseTool):
    """Tool for file operations (read, write, edit)."""

    name = "file_ops"
    description = "Read, write, and edit files"

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a file operation."""
        if operation == "read":
            return await self.read_file(**kwargs)
        elif operation == "write":
            return await self.write_file(**kwargs)
        elif operation == "edit":
            return await self.edit_file(**kwargs)
        elif operation == "list_dir":
            return await self.list_directory(**kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}

    async def read_file(
        self,
        file_path: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Read a file's contents."""
        try:
            path = Path(file_path)

            if path.is_dir():
                return await self.list_directory(file_path)

            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

            lines = content.split("\n")
            total_lines = len(lines)

            # Apply offset and limit
            start = offset - 1 if offset else 0
            end = start + limit if limit else len(lines)
            selected_lines = lines[start:end]

            # Format with line numbers
            formatted_lines = []
            for i, line in enumerate(selected_lines, start=start + 1):
                # Truncate long lines
                if len(line) > 2000:
                    line = line[:2000] + "..."
                formatted_lines.append(f"{i:6}\t{line}")

            return {
                "file_path": file_path,
                "content": "\n".join(formatted_lines),
                "total_lines": total_lines,
                "start_line": start + 1,
                "end_line": min(end, total_lines),
            }
        except UnicodeDecodeError:
            return {"error": f"Cannot read binary file: {file_path}"}
        except Exception as e:
            return {"error": str(e)}

    async def write_file(
        self, file_path: str, content: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            path = Path(file_path)

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(content)

            return {
                "success": True,
                "file_path": file_path,
                "message": f"File written successfully: {file_path}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def edit_file(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Edit a file by replacing a string."""
        try:
            path = Path(file_path)

            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

            # Check if old_string exists
            if old_string not in content:
                return {
                    "error": f"String not found in file: {old_string[:100]}..."
                    if len(old_string) > 100
                    else f"String not found in file: {old_string}"
                }

            # Check uniqueness if not replace_all
            if not replace_all and content.count(old_string) > 1:
                return {
                    "error": f"String appears {content.count(old_string)} times. Use replace_all=True or provide more context."
                }

            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
                count = content.count(old_string)
            else:
                new_content = content.replace(old_string, new_string, 1)
                count = 1

            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(new_content)

            return {
                "success": True,
                "file_path": file_path,
                "replacements": count,
                "message": f"Replaced {count} occurrence(s)",
            }
        except Exception as e:
            return {"error": str(e)}

    async def list_directory(
        self, path: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """List contents of a directory."""
        try:
            dir_path = Path(path)

            if not dir_path.exists():
                return {"error": f"Directory not found: {path}"}

            if not dir_path.is_dir():
                return {"error": f"Not a directory: {path}"}

            entries: List[Dict[str, Any]] = []
            for entry in sorted(dir_path.iterdir()):
                entry_info = {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "path": str(entry),
                }
                if entry.is_file():
                    entry_info["size"] = entry.stat().st_size
                entries.append(entry_info)

            return {
                "path": path,
                "entries": entries,
                "count": len(entries),
            }
        except Exception as e:
            return {"error": str(e)}

"""Git operations tool."""

import asyncio
from typing import Any, Dict, List, Optional
from app.tools.base import BaseTool


class GitTool(BaseTool):
    """Tool for git operations."""

    name = "git"
    description = "Perform git operations"

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a git operation."""
        operations = {
            "status": self.status,
            "diff": self.diff,
            "add": self.add,
            "commit": self.commit,
            "push": self.push,
            "pull": self.pull,
            "branch": self.branch,
            "checkout": self.checkout,
            "create_branch": self.create_branch,
            "log": self.log,
            "clone": self.clone,
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        return await operations[operation](**kwargs)

    async def _run_git(
        self, args: List[str], repo_path: str
    ) -> Dict[str, Any]:
        """Run a git command."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=repo_path,
            )

            stdout, stderr = await process.communicate()

            return {
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "return_code": process.returncode,
            }
        except Exception as e:
            return {"error": str(e)}

    async def status(self, repo_path: str, **kwargs: Any) -> Dict[str, Any]:
        """Get git status."""
        result = await self._run_git(["status", "--porcelain"], repo_path)
        if "error" in result:
            return result

        # Parse status output
        files = []
        for line in result["stdout"].strip().split("\n"):
            if line:
                status = line[:2]
                filename = line[3:]
                files.append({"status": status, "file": filename})

        # Get current branch
        branch_result = await self._run_git(
            ["rev-parse", "--abbrev-ref", "HEAD"], repo_path
        )
        branch = branch_result.get("stdout", "").strip()

        return {
            "branch": branch,
            "files": files,
            "clean": len(files) == 0,
        }

    async def diff(
        self,
        repo_path: str,
        staged: bool = False,
        file_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get git diff."""
        args = ["diff"]
        if staged:
            args.append("--staged")
        if file_path:
            args.append(file_path)

        return await self._run_git(args, repo_path)

    async def add(
        self,
        repo_path: str,
        files: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Stage files."""
        if files:
            args = ["add"] + files
        else:
            args = ["add", "-A"]

        result = await self._run_git(args, repo_path)
        if result.get("return_code") == 0:
            result["message"] = "Files staged successfully"
        return result

    async def commit(
        self, repo_path: str, message: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Commit staged changes."""
        result = await self._run_git(["commit", "-m", message], repo_path)
        if result.get("return_code") == 0:
            result["message"] = "Committed successfully"
        return result

    async def push(
        self,
        repo_path: str,
        branch: Optional[str] = None,
        set_upstream: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Push commits to remote."""
        args = ["push"]
        if set_upstream:
            args.extend(["-u", "origin"])
            if branch:
                args.append(branch)
        elif branch:
            args.extend(["origin", branch])

        return await self._run_git(args, repo_path)

    async def pull(
        self, repo_path: str, branch: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Pull from remote."""
        args = ["pull"]
        if branch:
            args.extend(["origin", branch])

        return await self._run_git(args, repo_path)

    async def branch(
        self, repo_path: str, list_all: bool = False, **kwargs: Any
    ) -> Dict[str, Any]:
        """List branches."""
        args = ["branch"]
        if list_all:
            args.append("-a")

        result = await self._run_git(args, repo_path)
        if "error" in result:
            return result

        branches = []
        current = None
        for line in result["stdout"].strip().split("\n"):
            if line:
                if line.startswith("*"):
                    current = line[2:].strip()
                    branches.append(current)
                else:
                    branches.append(line.strip())

        return {"branches": branches, "current": current}

    async def checkout(
        self, repo_path: str, branch: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Checkout a branch."""
        result = await self._run_git(["checkout", branch], repo_path)
        if result.get("return_code") == 0:
            result["message"] = f"Switched to branch '{branch}'"
        return result

    async def create_branch(
        self, repo_path: str, branch_name: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Create and checkout a new branch."""
        result = await self._run_git(["checkout", "-b", branch_name], repo_path)
        if result.get("return_code") == 0:
            result["message"] = f"Created and switched to branch '{branch_name}'"
        return result

    async def log(
        self,
        repo_path: str,
        limit: int = 10,
        oneline: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get git log."""
        args = ["log", f"-{limit}"]
        if oneline:
            args.append("--oneline")

        return await self._run_git(args, repo_path)

    async def clone(
        self, url: str, dest_path: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Clone a repository."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "clone",
                url,
                dest_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            return {
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "return_code": process.returncode,
                "path": dest_path,
            }
        except Exception as e:
            return {"error": str(e)}

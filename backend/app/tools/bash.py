"""Bash/Shell execution tool."""

import asyncio
import os
from typing import Any, Dict, Optional
from app.tools.base import BaseTool


class ShellSession:
    """Manages a persistent shell session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.process: Optional[asyncio.subprocess.Process] = None
        self.cwd = os.getcwd()

    async def start(self) -> None:
        """Start the shell process."""
        self.process = await asyncio.create_subprocess_shell(
            "/bin/bash",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
        )

    async def execute(
        self, command: str, exec_dir: str, timeout: int = 45000
    ) -> Dict[str, Any]:
        """Execute a command in the shell."""
        timeout_seconds = timeout / 1000

        # Change to the execution directory
        full_command = f"cd {exec_dir} && {command}"

        try:
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=exec_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout_seconds
                )
                return {
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                    "return_code": process.returncode,
                    "exec_dir": exec_dir,
                }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout_seconds} seconds",
                    "return_code": -1,
                    "exec_dir": exec_dir,
                    "timed_out": True,
                }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "exec_dir": exec_dir,
            }


class BashTool(BaseTool):
    """Tool for executing bash commands."""

    name = "bash"
    description = "Execute bash commands in a shell session"

    def __init__(self):
        self.sessions: Dict[str, ShellSession] = {}
        self.background_processes: Dict[str, asyncio.subprocess.Process] = {}

    def get_or_create_session(self, session_id: str = "default") -> ShellSession:
        """Get or create a shell session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = ShellSession(session_id)
        return self.sessions[session_id]

    async def execute(
        self,
        command: str,
        exec_dir: str,
        timeout: int = 45000,
        run_in_background: bool = False,
        bash_id: str = "default",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a bash command."""
        session = self.get_or_create_session(bash_id)

        if run_in_background:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=exec_dir,
            )
            process_id = f"{bash_id}_{len(self.background_processes)}"
            self.background_processes[process_id] = process
            return {
                "message": f"Command started in background with ID: {process_id}",
                "process_id": process_id,
            }

        return await session.execute(command, exec_dir, timeout)

    async def get_background_output(self, process_id: str) -> Dict[str, Any]:
        """Get output from a background process."""
        if process_id not in self.background_processes:
            return {"error": f"No background process with ID: {process_id}"}

        process = self.background_processes[process_id]
        if process.returncode is None:
            return {"status": "running", "message": "Process is still running"}

        stdout, stderr = await process.communicate()
        return {
            "status": "completed",
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "return_code": process.returncode,
        }

    async def kill_background_process(self, process_id: str) -> Dict[str, Any]:
        """Kill a background process."""
        if process_id not in self.background_processes:
            return {"error": f"No background process with ID: {process_id}"}

        process = self.background_processes[process_id]
        process.kill()
        del self.background_processes[process_id]
        return {"message": f"Process {process_id} killed"}

"""Screen recording tool for capturing browser and GUI interactions."""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.tools.base import BaseTool


class ScreenRecordingTool(BaseTool):
    """Tool for recording screen/browser interactions."""

    name = "screen_recording"
    description = "Record screen or browser interactions for documentation and testing"

    def __init__(self):
        self.recordings_dir = Path("/tmp/kevin-recordings")
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.active_recordings: Dict[str, Dict[str, Any]] = {}

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a screen recording operation."""
        operations = {
            "start": self.start_recording,
            "stop": self.stop_recording,
            "status": self.get_status,
            "list": self.list_recordings,
            "get": self.get_recording,
            "delete": self.delete_recording,
            "screenshot": self.take_screenshot,
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        return await operations[operation](**kwargs)

    async def start_recording(
        self,
        session_id: Optional[str] = None,
        name: Optional[str] = None,
        display: str = ":0",
        framerate: int = 30,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Start a screen recording.
        
        Args:
            session_id: Session ID to associate recording with
            name: Optional name for the recording
            display: X display to record (default :0)
            framerate: Recording framerate (default 30)
        """
        try:
            recording_id = str(uuid.uuid4())[:8]
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}_{recording_id}.mp4"
            filepath = self.recordings_dir / filename

            # Check if ffmpeg is available
            check_process = await asyncio.create_subprocess_exec(
                "which", "ffmpeg",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await check_process.communicate()

            if check_process.returncode != 0:
                return {
                    "error": "ffmpeg not installed. Screen recording requires ffmpeg.",
                    "suggestion": "Install ffmpeg with: apt-get install ffmpeg",
                }

            # Start ffmpeg recording process
            # Using x11grab for X11 display capture
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-y",  # Overwrite output
                "-f", "x11grab",
                "-framerate", str(framerate),
                "-i", display,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "23",
                str(filepath),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.active_recordings[recording_id] = {
                "id": recording_id,
                "name": name or f"Recording {timestamp}",
                "session_id": session_id,
                "filepath": str(filepath),
                "filename": filename,
                "started_at": datetime.utcnow().isoformat(),
                "status": "recording",
                "process": process,
                "display": display,
                "framerate": framerate,
            }

            return {
                "success": True,
                "recording_id": recording_id,
                "message": f"Recording started: {filename}",
                "filepath": str(filepath),
            }
        except Exception as e:
            return {"error": str(e)}

    async def stop_recording(
        self,
        recording_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Stop a screen recording.
        
        Args:
            recording_id: ID of recording to stop (stops most recent if not specified)
        """
        try:
            if not self.active_recordings:
                return {"error": "No active recordings"}

            # Get recording to stop
            if recording_id:
                if recording_id not in self.active_recordings:
                    return {"error": f"Recording not found: {recording_id}"}
                recording = self.active_recordings[recording_id]
            else:
                # Stop most recent recording
                recording_id = list(self.active_recordings.keys())[-1]
                recording = self.active_recordings[recording_id]

            process = recording.get("process")
            if process:
                # Send 'q' to ffmpeg to stop gracefully
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()

            recording["status"] = "completed"
            recording["stopped_at"] = datetime.utcnow().isoformat()
            del recording["process"]

            # Check if file was created
            filepath = Path(recording["filepath"])
            if filepath.exists():
                recording["file_size"] = filepath.stat().st_size
                recording["file_exists"] = True
            else:
                recording["file_exists"] = False

            # Move to completed recordings
            del self.active_recordings[recording_id]

            return {
                "success": True,
                "recording_id": recording_id,
                "filepath": recording["filepath"],
                "file_exists": recording.get("file_exists", False),
                "file_size": recording.get("file_size", 0),
                "duration": recording.get("stopped_at"),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_status(
        self,
        recording_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get status of recordings.
        
        Args:
            recording_id: Specific recording ID (optional)
        """
        try:
            if recording_id:
                if recording_id in self.active_recordings:
                    recording = self.active_recordings[recording_id].copy()
                    if "process" in recording:
                        del recording["process"]
                    return {"success": True, "recording": recording}
                return {"error": f"Recording not found: {recording_id}"}

            active = []
            for rid, rec in self.active_recordings.items():
                rec_copy = rec.copy()
                if "process" in rec_copy:
                    del rec_copy["process"]
                active.append(rec_copy)

            return {
                "success": True,
                "active_recordings": active,
                "count": len(active),
            }
        except Exception as e:
            return {"error": str(e)}

    async def list_recordings(
        self,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List all recordings.
        
        Args:
            session_id: Filter by session ID (optional)
        """
        try:
            recordings = []
            for filepath in self.recordings_dir.glob("*.mp4"):
                stat = filepath.stat()
                recording = {
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
                recordings.append(recording)

            # Sort by creation time, newest first
            recordings.sort(key=lambda x: x["created_at"], reverse=True)

            return {
                "success": True,
                "recordings": recordings,
                "count": len(recordings),
                "directory": str(self.recordings_dir),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_recording(
        self,
        recording_id: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get a specific recording file.
        
        Args:
            recording_id: Recording ID
            filename: Or filename directly
        """
        try:
            if filename:
                filepath = self.recordings_dir / filename
            elif recording_id:
                # Search for file with recording_id in name
                matches = list(self.recordings_dir.glob(f"*{recording_id}*.mp4"))
                if not matches:
                    return {"error": f"Recording not found: {recording_id}"}
                filepath = matches[0]
            else:
                return {"error": "Provide recording_id or filename"}

            if not filepath.exists():
                return {"error": f"File not found: {filepath}"}

            stat = filepath.stat()
            return {
                "success": True,
                "filename": filepath.name,
                "filepath": str(filepath),
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def delete_recording(
        self,
        recording_id: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Delete a recording.
        
        Args:
            recording_id: Recording ID
            filename: Or filename directly
        """
        try:
            if filename:
                filepath = self.recordings_dir / filename
            elif recording_id:
                matches = list(self.recordings_dir.glob(f"*{recording_id}*.mp4"))
                if not matches:
                    return {"error": f"Recording not found: {recording_id}"}
                filepath = matches[0]
            else:
                return {"error": "Provide recording_id or filename"}

            if not filepath.exists():
                return {"error": f"File not found: {filepath}"}

            filepath.unlink()
            return {
                "success": True,
                "message": f"Deleted: {filepath.name}",
            }
        except Exception as e:
            return {"error": str(e)}

    async def take_screenshot(
        self,
        name: Optional[str] = None,
        display: str = ":0",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Take a screenshot.
        
        Args:
            name: Optional name for the screenshot
            display: X display to capture (default :0)
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            screenshot_id = str(uuid.uuid4())[:8]
            filename = f"screenshot_{timestamp}_{screenshot_id}.png"
            filepath = self.recordings_dir / filename

            # Try using scrot or import (ImageMagick)
            for cmd in [["scrot", str(filepath)], ["import", "-window", "root", str(filepath)]]:
                try:
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        env={**os.environ, "DISPLAY": display},
                    )
                    await process.communicate()
                    if process.returncode == 0 and filepath.exists():
                        return {
                            "success": True,
                            "filename": filename,
                            "filepath": str(filepath),
                            "size": filepath.stat().st_size,
                        }
                except FileNotFoundError:
                    continue

            # Fallback: try ffmpeg single frame capture
            process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-y",
                "-f", "x11grab",
                "-i", display,
                "-frames:v", "1",
                str(filepath),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()

            if filepath.exists():
                return {
                    "success": True,
                    "filename": filename,
                    "filepath": str(filepath),
                    "size": filepath.stat().st_size,
                }

            return {
                "error": "Failed to take screenshot. Install scrot, imagemagick, or ffmpeg.",
            }
        except Exception as e:
            return {"error": str(e)}

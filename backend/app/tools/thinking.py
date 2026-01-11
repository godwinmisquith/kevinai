"""Thinking tool for reasoning and reflection."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.tools.base import BaseTool


class ThinkingTool(BaseTool):
    """Tool for recording thoughts and reasoning."""

    name = "thinking"
    description = "Record thoughts, reasoning, and reflections during task execution"

    def __init__(self):
        self.thought_logs: Dict[str, List[Dict[str, Any]]] = {}

    async def execute(
        self,
        thought: str,
        session_id: Optional[str] = None,
        category: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Record a thought."""
        try:
            session_key = session_id or "default"

            if session_key not in self.thought_logs:
                self.thought_logs[session_key] = []

            thought_entry = {
                "id": len(self.thought_logs[session_key]) + 1,
                "thought": thought,
                "category": category or "general",
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.thought_logs[session_key].append(thought_entry)

            return {
                "success": True,
                "message": "Thought recorded",
                "thought_id": thought_entry["id"],
                "category": thought_entry["category"],
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_thoughts(
        self,
        session_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get recorded thoughts."""
        try:
            session_key = session_id or "default"
            thoughts = self.thought_logs.get(session_key, [])

            if category:
                thoughts = [t for t in thoughts if t["category"] == category]

            return {
                "success": True,
                "thoughts": thoughts[-limit:],
                "total_count": len(thoughts),
            }
        except Exception as e:
            return {"error": str(e)}

    async def clear_thoughts(
        self,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Clear recorded thoughts."""
        try:
            session_key = session_id or "default"
            count = len(self.thought_logs.get(session_key, []))
            self.thought_logs[session_key] = []

            return {
                "success": True,
                "message": f"Cleared {count} thoughts",
            }
        except Exception as e:
            return {"error": str(e)}

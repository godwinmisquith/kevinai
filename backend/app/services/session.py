"""Session management service."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from app.models.session import Session, Message, MessageRole, Todo, TodoStatus


class SessionService:
    """Service for managing sessions."""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(
        self,
        name: Optional[str] = None,
        workspace_path: Optional[str] = None,
    ) -> Session:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            name=name or f"Session {len(self.sessions) + 1}",
            workspace_path=workspace_path,
            messages=[],
            todos=[],
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[Session]:
        """List all sessions."""
        return list(self.sessions.values())

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        tool_calls: Optional[List[dict]] = None,
        tool_call_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[Message]:
        """Add a message to a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        message = Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            metadata=metadata,
        )
        session.messages.append(message)
        session.updated_at = datetime.now()
        return message

    def get_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a session."""
        session = self.get_session(session_id)
        return session.messages if session else []

    def update_todos(
        self, session_id: str, todos: List[Dict[str, str]]
    ) -> Optional[List[Todo]]:
        """Update todos for a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        session.todos = [
            Todo(
                content=t["content"],
                status=TodoStatus(t.get("status", "pending")),
            )
            for t in todos
        ]
        session.updated_at = datetime.now()
        return session.todos

    def get_todos(self, session_id: str) -> List[Todo]:
        """Get todos for a session."""
        session = self.get_session(session_id)
        return session.todos if session else []

    def get_conversation_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Get conversation history in LLM format."""
        messages = self.get_messages(session_id)

        if limit:
            messages = messages[-limit:]

        history = []
        for msg in messages:
            entry: Dict[str, str] = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            history.append(entry)

        return history

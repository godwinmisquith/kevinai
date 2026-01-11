"""Session and message models."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class TodoStatus(str, Enum):
    """Todo status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Todo(BaseModel):
    """Todo item model."""

    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    content: str
    status: TodoStatus = TodoStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Message(BaseModel):
    """Chat message model."""

    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    role: MessageRole
    content: str
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = None


class Session(BaseModel):
    """Session model."""

    id: str
    name: str = "New Session"
    messages: List[Message] = Field(default_factory=list)
    todos: List[Todo] = Field(default_factory=list)
    workspace_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = None


class SessionCreate(BaseModel):
    """Session creation request."""

    name: Optional[str] = "New Session"
    workspace_path: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model."""

    session_id: str
    message: str
    attachments: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """Chat response model."""

    session_id: str
    message: Message
    tool_results: Optional[List[Any]] = None

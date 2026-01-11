"""API routes for Kevin AI."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.llm import LLMService
from app.services.session import SessionService
from app.services.agent import AgentService

router = APIRouter()

# Initialize services
llm_service = LLMService()
session_service = SessionService()
agent_service = AgentService(llm_service, session_service)


# Request/Response models
class CreateSessionRequest(BaseModel):
    name: Optional[str] = None
    workspace_path: Optional[str] = None


class ChatRequest(BaseModel):
    message: str


class TodoItem(BaseModel):
    content: str
    status: str = "pending"


class UpdateTodosRequest(BaseModel):
    todos: List[TodoItem]


class ToolExecuteRequest(BaseModel):
    tool_name: str
    args: Dict[str, Any]


# Session endpoints
@router.post("/sessions")
async def create_session(request: CreateSessionRequest) -> Dict[str, Any]:
    """Create a new session."""
    session = session_service.create_session(
        name=request.name,
        workspace_path=request.workspace_path,
    )
    return {
        "id": session.id,
        "name": session.name,
        "workspace_path": session.workspace_path,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/sessions")
async def list_sessions() -> List[Dict[str, Any]]:
    """List all sessions."""
    sessions = session_service.list_sessions()
    return [
        {
            "id": s.id,
            "name": s.name,
            "workspace_path": s.workspace_path,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
            "message_count": len(s.messages),
            "todo_count": len(s.todos),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """Get a session by ID."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "name": session.name,
        "workspace_path": session.workspace_path,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "tool_calls": m.tool_calls,
                "created_at": m.created_at.isoformat(),
            }
            for m in session.messages
        ],
        "todos": [
            {
                "id": t.id,
                "content": t.content,
                "status": t.status.value,
            }
            for t in session.todos
        ],
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """Delete a session."""
    if session_service.delete_session(session_id):
        return {"message": "Session deleted"}
    raise HTTPException(status_code=404, detail="Session not found")


# Chat endpoints
@router.post("/sessions/{session_id}/chat")
async def chat(session_id: str, request: ChatRequest) -> Dict[str, Any]:
    """Send a message and get a response."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await agent_service.process_message(session_id, request.message)
    return result


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a session."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return [
        {
            "id": m.id,
            "role": m.role.value,
            "content": m.content,
            "tool_calls": m.tool_calls,
            "created_at": m.created_at.isoformat(),
        }
        for m in session.messages
    ]


# Todo endpoints
@router.get("/sessions/{session_id}/todos")
async def get_todos(session_id: str) -> List[Dict[str, Any]]:
    """Get todos for a session."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return [
        {
            "id": t.id,
            "content": t.content,
            "status": t.status.value,
        }
        for t in session.todos
    ]


@router.put("/sessions/{session_id}/todos")
async def update_todos(
    session_id: str, request: UpdateTodosRequest
) -> List[Dict[str, Any]]:
    """Update todos for a session."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    todos = session_service.update_todos(
        session_id, [{"content": t.content, "status": t.status} for t in request.todos]
    )

    return [
        {
            "id": t.id,
            "content": t.content,
            "status": t.status.value,
        }
        for t in (todos or [])
    ]


# Tool execution endpoint
@router.post("/sessions/{session_id}/tools/execute")
async def execute_tool(
    session_id: str, request: ToolExecuteRequest
) -> Dict[str, Any]:
    """Execute a tool directly."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await agent_service._execute_tool(
        session_id, request.tool_name, request.args
    )
    return result


# WebSocket for real-time updates
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()

    session = session_service.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "chat":
                message = data.get("message", "")
                result = await agent_service.process_message(session_id, message)

                await websocket.send_json(
                    {
                        "type": "response",
                        "data": result,
                    }
                )

            elif data.get("type") == "tool":
                tool_name = data.get("tool_name")
                args = data.get("args", {})
                result = await agent_service._execute_tool(session_id, tool_name, args)

                await websocket.send_json(
                    {
                        "type": "tool_result",
                        "tool": tool_name,
                        "data": result,
                    }
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})


# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "kevin-ai"}

"""API routes for Kevin AI."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.llm import LLMService
from app.services.session import SessionService
from app.services.agent import AgentService
from app.services.model_router import model_router, ModelTier

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


class ChatWithModelRequest(BaseModel):
    message: str
    model: Optional[str] = None
    force_tier: Optional[str] = None


class CostEstimateRequest(BaseModel):
    message: str
    estimated_output_tokens: int = 500


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


# Cost tracking endpoints
@router.get("/costs")
async def get_all_costs() -> Dict[str, Any]:
    """Get cost summary across all sessions."""
    return model_router.get_all_costs()


@router.get("/sessions/{session_id}/costs")
async def get_session_costs(session_id: str) -> Dict[str, Any]:
    """Get cost summary for a specific session."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return model_router.get_session_costs(session_id)


@router.post("/costs/estimate")
async def estimate_cost(request: CostEstimateRequest) -> Dict[str, Any]:
    """Estimate cost for a message before sending."""
    return model_router.estimate_cost(
        message=request.message,
        estimated_output_tokens=request.estimated_output_tokens,
    )


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available models and their tiers."""
    from app.config import settings

    return {
        "tiers": {
            "fast": {
                "description": "For simple tasks (file reads, basic queries, formatting)",
                "openai": settings.fast_model_openai,
                "anthropic": settings.fast_model_anthropic,
                "max_tokens": settings.fast_model_max_tokens,
            },
            "standard": {
                "description": "For most coding tasks and analysis",
                "openai": settings.standard_model_openai,
                "anthropic": settings.standard_model_anthropic,
                "max_tokens": settings.standard_model_max_tokens,
            },
            "premium": {
                "description": "For complex reasoning and architecture",
                "openai": settings.premium_model_openai,
                "anthropic": settings.premium_model_anthropic,
                "max_tokens": settings.premium_model_max_tokens,
            },
        },
        "default_model": settings.default_model,
        "cost_tracking_enabled": settings.enable_cost_tracking,
        "model_costs": settings.model_costs,
    }


@router.post("/sessions/{session_id}/chat/advanced")
async def chat_with_model_selection(
    session_id: str, request: ChatWithModelRequest
) -> Dict[str, Any]:
    """Send a message with explicit model/tier selection."""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Convert tier string to enum if provided
    force_tier = None
    if request.force_tier:
        tier_map = {
            "fast": ModelTier.FAST,
            "standard": ModelTier.STANDARD,
            "premium": ModelTier.PREMIUM,
        }
        force_tier = tier_map.get(request.force_tier.lower())

    # Get conversation history
    history = session_service.get_conversation_history(session_id)

    # Add user message
    from app.models.session import MessageRole
    session_service.add_message(session_id, MessageRole.USER, request.message)
    history.append({"role": "user", "content": request.message})

    # Get LLM response with model selection
    result = await llm_service.chat_completion(
        messages=history,
        model=request.model,
        session_id=session_id,
        force_tier=force_tier,
    )

    # Add assistant response
    session_service.add_message(
        session_id,
        MessageRole.ASSISTANT,
        result.get("content", ""),
        tool_calls=result.get("tool_calls"),
    )

    return {
        "message": result.get("content", ""),
        "model_used": result.get("model_used"),
        "usage": result.get("usage"),
        "tool_calls": result.get("tool_calls"),
    }


# MCP Marketplace endpoints
@router.get("/mcp/marketplace")
async def mcp_marketplace_list(
    category: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> Dict[str, Any]:
    """List all MCP servers in the marketplace."""
    result = await agent_service.mcp_tool.execute(
        command="marketplace_list",
        category=category,
        page=page,
        per_page=per_page,
    )
    return result


@router.get("/mcp/marketplace/search")
async def mcp_marketplace_search(query: str) -> Dict[str, Any]:
    """Search the MCP marketplace."""
    result = await agent_service.mcp_tool.execute(
        command="marketplace_search",
        query=query,
    )
    return result


@router.get("/mcp/marketplace/categories")
async def mcp_marketplace_categories() -> Dict[str, Any]:
    """List all MCP marketplace categories."""
    result = await agent_service.mcp_tool.execute(command="marketplace_categories")
    return result


@router.get("/mcp/marketplace/featured")
async def mcp_marketplace_featured() -> Dict[str, Any]:
    """Get featured MCP servers."""
    result = await agent_service.mcp_tool.execute(command="marketplace_featured")
    return result


@router.get("/mcp/marketplace/{server_id}")
async def mcp_marketplace_get(server_id: str) -> Dict[str, Any]:
    """Get details of a specific MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="marketplace_get",
        server_id=server_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


class MCPInstallRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None


@router.post("/mcp/servers/{server_id}/install")
async def mcp_install_server(
    server_id: str,
    request: MCPInstallRequest = MCPInstallRequest(),
) -> Dict[str, Any]:
    """Install an MCP server from the marketplace."""
    result = await agent_service.mcp_tool.execute(
        command="install",
        server_id=server_id,
        config=request.config,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/mcp/servers/{server_id}")
async def mcp_uninstall_server(server_id: str) -> Dict[str, Any]:
    """Uninstall an MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="uninstall",
        server_id=server_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


class MCPConfigureRequest(BaseModel):
    config: Dict[str, Any]


@router.put("/mcp/servers/{server_id}/configure")
async def mcp_configure_server(
    server_id: str,
    request: MCPConfigureRequest,
) -> Dict[str, Any]:
    """Configure an installed MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="configure",
        server_id=server_id,
        config=request.config,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/mcp/servers/{server_id}/config")
async def mcp_get_server_config(server_id: str) -> Dict[str, Any]:
    """Get configuration for an installed MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="get_config",
        server_id=server_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/mcp/servers")
async def mcp_list_installed() -> Dict[str, Any]:
    """List all installed MCP servers."""
    result = await agent_service.mcp_tool.execute(command="list_installed")
    return result


@router.get("/mcp/servers/{server_id}/tools")
async def mcp_list_tools(server_id: str) -> Dict[str, Any]:
    """List tools available on an MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="list_tools",
        server=server_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/mcp/servers/{server_id}/connect")
async def mcp_connect_server(server_id: str) -> Dict[str, Any]:
    """Connect to an MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="connect",
        server=server_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/mcp/servers/{server_id}/disconnect")
async def mcp_disconnect_server(server_id: str) -> Dict[str, Any]:
    """Disconnect from an MCP server."""
    result = await agent_service.mcp_tool.execute(
        command="disconnect",
        server=server_id,
    )
    return result


# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "kevin-ai"}

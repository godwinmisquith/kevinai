"""Task management tool (todos)."""

from typing import Any, Dict, List, Optional
from app.tools.base import BaseTool
from app.models.session import Todo, TodoStatus


class TaskTool(BaseTool):
    """Tool for task/todo management."""

    name = "task"
    description = "Manage todos and tasks"

    def __init__(self):
        self.todos: Dict[str, List[Todo]] = {}  # session_id -> todos

    async def execute(
        self, operation: str, session_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a task operation."""
        if operation == "write":
            return await self.write_todos(session_id, **kwargs)
        elif operation == "get":
            return await self.get_todos(session_id)
        elif operation == "update":
            return await self.update_todo(session_id, **kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}

    async def write_todos(
        self, session_id: str, todos: List[Dict[str, Any]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Write/update the todo list."""
        try:
            new_todos = []
            for todo_data in todos:
                todo = Todo(
                    content=todo_data["content"],
                    status=TodoStatus(todo_data.get("status", "pending")),
                )
                new_todos.append(todo)

            self.todos[session_id] = new_todos

            return {
                "success": True,
                "todos": [
                    {"content": t.content, "status": t.status.value}
                    for t in new_todos
                ],
                "count": len(new_todos),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_todos(self, session_id: str) -> Dict[str, Any]:
        """Get the current todo list."""
        todos = self.todos.get(session_id, [])
        return {
            "todos": [
                {
                    "id": t.id,
                    "content": t.content,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat(),
                }
                for t in todos
            ],
            "count": len(todos),
        }

    async def update_todo(
        self,
        session_id: str,
        todo_id: str,
        status: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update a specific todo."""
        todos = self.todos.get(session_id, [])

        for todo in todos:
            if todo.id == todo_id:
                if status:
                    todo.status = TodoStatus(status)
                if content:
                    todo.content = content
                return {
                    "success": True,
                    "todo": {
                        "id": todo.id,
                        "content": todo.content,
                        "status": todo.status.value,
                    },
                }

        return {"error": f"Todo not found: {todo_id}"}

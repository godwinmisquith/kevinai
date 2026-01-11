"""Agent service for orchestrating tools and LLM."""

import json
from typing import Any, Dict, List
from app.services.llm import LLMService
from app.services.session import SessionService
from app.tools.bash import BashTool
from app.tools.file_ops import FileOpsTool
from app.tools.search import SearchTool
from app.tools.browser import BrowserTool
from app.tools.git import GitTool
from app.tools.web import WebTool
from app.tools.task import TaskTool
from app.models.session import MessageRole


class AgentService:
    """Service for orchestrating the AI agent."""

    def __init__(
        self,
        llm_service: LLMService,
        session_service: SessionService,
    ):
        self.llm = llm_service
        self.sessions = session_service

        # Initialize tools
        self.bash_tool = BashTool()
        self.file_tool = FileOpsTool()
        self.search_tool = SearchTool()
        self.browser_tool = BrowserTool()
        self.git_tool = GitTool()
        self.web_tool = WebTool()
        self.task_tool = TaskTool()

    async def process_message(
        self,
        session_id: str,
        user_message: str,
        max_iterations: int = 10,
    ) -> Dict[str, Any]:
        """Process a user message and execute tools as needed."""
        # Add user message to session
        self.sessions.add_message(session_id, MessageRole.USER, user_message)

        # Get conversation history
        history = self.sessions.get_conversation_history(session_id)

        iterations = 0
        tool_results: List[Dict[str, Any]] = []

        while iterations < max_iterations:
            iterations += 1

            # Get LLM response
            response = await self.llm.chat_completion(history)

            # Add assistant message
            self.sessions.add_message(
                session_id,
                MessageRole.ASSISTANT,
                response.get("content", ""),
                tool_calls=response.get("tool_calls"),
            )

            # Check if there are tool calls
            tool_calls = response.get("tool_calls", [])
            if not tool_calls:
                # No more tool calls, return final response
                return {
                    "message": response.get("content", ""),
                    "tool_results": tool_results,
                    "iterations": iterations,
                }

            # Execute tool calls
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                try:
                    args = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                # Execute the tool
                result = await self._execute_tool(session_id, tool_name, args)
                tool_results.append(
                    {
                        "tool": tool_name,
                        "args": args,
                        "result": result,
                    }
                )

                # Add tool result to history
                tool_result_content = json.dumps(result, indent=2)
                self.sessions.add_message(
                    session_id,
                    MessageRole.TOOL,
                    tool_result_content,
                    tool_call_id=tool_call["id"],
                )

            # Update history for next iteration
            history = self.sessions.get_conversation_history(session_id)

        return {
            "message": "Max iterations reached",
            "tool_results": tool_results,
            "iterations": iterations,
        }

    async def _execute_tool(
        self, session_id: str, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool by name."""
        try:
            if tool_name == "bash":
                return await self.bash_tool.run(**args)

            elif tool_name == "read_file":
                return await self.file_tool.run(operation="read", **args)

            elif tool_name == "write_file":
                return await self.file_tool.run(operation="write", **args)

            elif tool_name == "edit_file":
                return await self.file_tool.run(operation="edit", **args)

            elif tool_name == "glob":
                return await self.search_tool.run(operation="glob", **args)

            elif tool_name == "grep":
                return await self.search_tool.run(operation="grep", **args)

            elif tool_name == "browser_navigate":
                return await self.browser_tool.run(operation="navigate", **args)

            elif tool_name == "browser_click":
                return await self.browser_tool.run(operation="click", **args)

            elif tool_name == "browser_type":
                return await self.browser_tool.run(operation="type", **args)

            elif tool_name == "browser_screenshot":
                return await self.browser_tool.run(operation="screenshot", **args)

            elif tool_name == "git_status":
                return await self.git_tool.run(operation="status", **args)

            elif tool_name == "git_commit":
                # First add, then commit
                add_result = await self.git_tool.run(
                    operation="add",
                    repo_path=args["repo_path"],
                    files=args.get("files"),
                )
                if add_result.get("success"):
                    return await self.git_tool.run(operation="commit", **args)
                return add_result

            elif tool_name == "git_create_branch":
                return await self.git_tool.run(operation="create_branch", **args)

            elif tool_name == "git_push":
                return await self.git_tool.run(operation="push", **args)

            elif tool_name == "git_create_pr":
                # This would need GitHub API integration
                return {
                    "success": False,
                    "message": "PR creation requires GitHub API integration",
                }

            elif tool_name == "web_search":
                return await self.web_tool.run(operation="search", **args)

            elif tool_name == "web_get_contents":
                return await self.web_tool.run(operation="get_contents", **args)

            elif tool_name == "todo_write":
                # Update session todos
                todos = args.get("todos", [])
                self.sessions.update_todos(session_id, todos)
                return await self.task_tool.run(
                    operation="write", session_id=session_id, **args
                )

            elif tool_name == "message_user":
                # Just return the message - it will be shown to user
                return {
                    "success": True,
                    "message": args.get("message", ""),
                    "block_on_user": args.get("block_on_user", False),
                }

            elif tool_name == "think":
                # Just record the thought
                return {
                    "success": True,
                    "thought": args.get("thought", ""),
                }

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.browser_tool.close()
        await self.web_tool.close()

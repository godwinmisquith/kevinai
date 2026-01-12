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
from app.tools.data_analyst import DataAnalystTool
from app.tools.deploy import DeployTool
from app.tools.lsp import LSPTool
from app.tools.mcp import MCPTool
from app.tools.thinking import ThinkingTool
from app.tools.github_api import GitHubAPITool
from app.tools.screen_recording import ScreenRecordingTool
from app.tools.code_validator import CodeValidatorTool
from app.tools.knowledge import KnowledgeTool
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

        # Initialize core tools
        self.bash_tool = BashTool()
        self.file_tool = FileOpsTool()
        self.search_tool = SearchTool()
        self.browser_tool = BrowserTool()
        self.git_tool = GitTool()
        self.web_tool = WebTool()
        self.task_tool = TaskTool()

        # Initialize advanced tools
        self.data_analyst_tool = DataAnalystTool()
        self.deploy_tool = DeployTool()
        self.lsp_tool = LSPTool()
        self.mcp_tool = MCPTool()
        self.thinking_tool = ThinkingTool()
        self.github_api_tool = GitHubAPITool()
        self.screen_recording_tool = ScreenRecordingTool()
        self.code_validator_tool = CodeValidatorTool()
        self.knowledge_tool = KnowledgeTool()

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
                # Record the thought using thinking tool
                return await self.thinking_tool.execute(
                    thought=args.get("thought", ""),
                    session_id=session_id,
                    category=args.get("category"),
                )

            # Data Analyst tools
            elif tool_name == "data_analyst":
                operation = args.pop("operation", "analyze")
                return await self.data_analyst_tool.execute(operation=operation, **args)

            # Deploy tools
            elif tool_name == "deploy":
                operation = args.pop("operation", "status")
                return await self.deploy_tool.execute(operation=operation, **args)

            # LSP tools
            elif tool_name == "lsp_tool":
                operation = args.pop("operation", "get_diagnostics")
                return await self.lsp_tool.execute(operation=operation, **args)

            elif tool_name == "goto_definition":
                return await self.lsp_tool.execute(operation="goto_definition", **args)

            elif tool_name == "find_references":
                return await self.lsp_tool.execute(operation="find_references", **args)

            elif tool_name == "hover_symbol":
                return await self.lsp_tool.execute(operation="hover_symbol", **args)

            elif tool_name == "get_diagnostics":
                return await self.lsp_tool.execute(operation="get_diagnostics", **args)

            # MCP tools
            elif tool_name == "mcp_tool":
                operation = args.pop("operation", "list_servers")
                return await self.mcp_tool.execute(operation=operation, **args)

            elif tool_name == "mcp_list_servers":
                return await self.mcp_tool.execute(operation="list_servers", **args)

            elif tool_name == "mcp_list_tools":
                return await self.mcp_tool.execute(operation="list_tools", **args)

            elif tool_name == "mcp_call_tool":
                return await self.mcp_tool.execute(operation="call_tool", **args)

            # GitHub API tools
            elif tool_name == "github_api":
                operation = args.pop("operation", "list_repos")
                return await self.github_api_tool.execute(operation=operation, **args)

            elif tool_name == "git_create_pr":
                return await self.github_api_tool.execute(operation="create_pr", **args)

            elif tool_name == "git_view_pr":
                return await self.github_api_tool.execute(operation="view_pr", **args)

            elif tool_name == "git_pr_checks":
                return await self.github_api_tool.execute(operation="pr_checks", **args)

            elif tool_name == "git_comment_on_pr":
                return await self.github_api_tool.execute(operation="comment_on_pr", **args)

            elif tool_name == "git_ci_job_logs":
                return await self.github_api_tool.execute(operation="ci_job_logs", **args)

            # Screen recording tools
            elif tool_name == "recording_start":
                return await self.screen_recording_tool.execute(
                    operation="start", session_id=session_id, **args
                )

            elif tool_name == "recording_stop":
                return await self.screen_recording_tool.execute(operation="stop", **args)

            elif tool_name == "screenshot":
                return await self.screen_recording_tool.execute(operation="screenshot", **args)

            # Code validation tools
            elif tool_name == "code_validator":
                operation = args.pop("operation", "validate_all")
                return await self.code_validator_tool.execute(operation=operation, **args)

            elif tool_name == "validate_code":
                return await self.code_validator_tool.execute(operation="validate_all", **args)

            elif tool_name == "lint_code":
                return await self.code_validator_tool.execute(operation="lint", **args)

            elif tool_name == "type_check":
                return await self.code_validator_tool.execute(operation="type_check", **args)

            elif tool_name == "run_tests":
                return await self.code_validator_tool.execute(operation="test", **args)

            elif tool_name == "build_project":
                return await self.code_validator_tool.execute(operation="build", **args)

            elif tool_name == "detect_project":
                return await self.code_validator_tool.execute(operation="detect_project", **args)

            elif tool_name == "syntax_check":
                return await self.code_validator_tool.execute(operation="syntax_check", **args)

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.browser_tool.close()
        await self.web_tool.close()

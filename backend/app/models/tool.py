"""Tool models."""

from typing import Any, Optional, List
from pydantic import BaseModel
from enum import Enum


class ToolType(str, Enum):
    """Tool type enum."""

    BASH = "bash"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EDIT_FILE = "edit_file"
    GLOB = "glob"
    GREP = "grep"
    LSP = "lsp"
    BROWSER_NAVIGATE = "browser_navigate"
    BROWSER_CLICK = "browser_click"
    BROWSER_TYPE = "browser_type"
    BROWSER_SCROLL = "browser_scroll"
    BROWSER_VIEW = "browser_view"
    BROWSER_SCREENSHOT = "browser_screenshot"
    GIT_STATUS = "git_status"
    GIT_COMMIT = "git_commit"
    GIT_PUSH = "git_push"
    GIT_CREATE_PR = "git_create_pr"
    GIT_VIEW_PR = "git_view_pr"
    WEB_SEARCH = "web_search"
    WEB_GET_CONTENTS = "web_get_contents"
    TODO_WRITE = "todo_write"
    MESSAGE_USER = "message_user"
    THINK = "think"


class ToolCall(BaseModel):
    """Tool call model."""

    id: str
    tool_type: ToolType
    parameters: dict
    session_id: str


class ToolResult(BaseModel):
    """Tool result model."""

    tool_call_id: str
    tool_type: ToolType
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class ToolDefinition(BaseModel):
    """Tool definition for LLM."""

    name: str
    description: str
    parameters: dict


# Tool definitions for the LLM
TOOL_DEFINITIONS: List[dict] = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command in a shell session. Use this for running commands, installing packages, running tests, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    },
                    "exec_dir": {
                        "type": "string",
                        "description": "The directory to execute the command in",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds (default: 45000)",
                    },
                    "run_in_background": {
                        "type": "boolean",
                        "description": "Whether to run the command in the background",
                    },
                },
                "required": ["command", "exec_dir"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Use this to view file contents before editing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to read",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Line number to start reading from (optional)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of lines to read (optional)",
                    },
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if it doesn't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing a specific string with another. The old_string must be unique in the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to edit",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact string to replace",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The string to replace it with",
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "Whether to replace all occurrences (default: false)",
                    },
                },
                "required": ["file_path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files matching a glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The glob pattern to match (e.g., '**/*.py')",
                    },
                    "path": {
                        "type": "string",
                        "description": "The directory to search in",
                    },
                },
                "required": ["pattern", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for a pattern in files using ripgrep.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The regex pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "The file or directory to search in",
                    },
                    "glob": {
                        "type": "string",
                        "description": "Glob pattern to filter files (optional)",
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Whether to ignore case (default: false)",
                    },
                },
                "required": ["pattern", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navigate to a URL in the browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to",
                    },
                    "tab_idx": {
                        "type": "integer",
                        "description": "Browser tab index (optional)",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Click an element in the browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector or element ID to click",
                    },
                    "coordinates": {
                        "type": "string",
                        "description": "x,y coordinates as fallback",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_type",
            "description": "Type text into an element in the browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector or element ID to type into",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text to type",
                    },
                    "press_enter": {
                        "type": "boolean",
                        "description": "Whether to press enter after typing",
                    },
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_screenshot",
            "description": "Take a screenshot of the current browser page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "full_page": {
                        "type": "boolean",
                        "description": "Whether to capture the full page",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Get the current git status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository",
                    },
                },
                "required": ["repo_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Stage and commit changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository",
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message",
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to stage (optional, stages all if not provided)",
                    },
                },
                "required": ["repo_path", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_create_branch",
            "description": "Create and checkout a new git branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository",
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the new branch",
                    },
                },
                "required": ["repo_path", "branch_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_push",
            "description": "Push commits to remote.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository",
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch to push (optional)",
                    },
                },
                "required": ["repo_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_create_pr",
            "description": "Create a pull request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in owner/repo format",
                    },
                    "title": {
                        "type": "string",
                        "description": "PR title",
                    },
                    "head_branch": {
                        "type": "string",
                        "description": "Branch to merge from",
                    },
                    "base_branch": {
                        "type": "string",
                        "description": "Branch to merge into",
                    },
                    "body": {
                        "type": "string",
                        "description": "PR description",
                    },
                },
                "required": ["repo", "title", "head_branch", "base_branch"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_get_contents",
            "description": "Fetch the contents of a web page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "URLs to fetch content from",
                    },
                },
                "required": ["urls"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo_write",
            "description": "Update the todo list for task management.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["content", "status"],
                        },
                        "description": "The updated todo list",
                    },
                },
                "required": ["todos"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "message_user",
            "description": "Send a message to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send",
                    },
                    "block_on_user": {
                        "type": "boolean",
                        "description": "Whether to wait for user response",
                    },
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File paths to attach",
                    },
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": "Think about something. Use this for complex reasoning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "The thought to record",
                    },
                },
                "required": ["thought"],
            },
        },
    },
]

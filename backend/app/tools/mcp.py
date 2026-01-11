"""MCP (Model Context Protocol) tool for integrating with external services."""

import asyncio
import json
from typing import Any, Dict, Optional

from app.tools.base import BaseTool


class MCPTool(BaseTool):
    """Tool for Model Context Protocol operations."""

    name = "mcp"
    description = "Interact with MCP servers for external service integrations"

    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Any] = {}
        self._register_default_servers()

    def _register_default_servers(self) -> None:
        """Register default MCP server configurations."""
        self.servers = {
            "slack": {
                "name": "Slack",
                "description": "Send messages and manage Slack channels",
                "tools": [
                    {"name": "send_message", "description": "Send a message to a channel"},
                    {"name": "list_channels", "description": "List available channels"},
                    {"name": "get_messages", "description": "Get recent messages from a channel"},
                    {"name": "create_channel", "description": "Create a new channel"},
                ],
                "resources": [
                    {"uri": "slack://channels", "description": "List of channels"},
                    {"uri": "slack://users", "description": "List of users"},
                ],
            },
            "linear": {
                "name": "Linear",
                "description": "Manage Linear issues and projects",
                "tools": [
                    {"name": "create_issue", "description": "Create a new issue"},
                    {"name": "update_issue", "description": "Update an existing issue"},
                    {"name": "list_issues", "description": "List issues"},
                    {"name": "get_issue", "description": "Get issue details"},
                    {"name": "list_projects", "description": "List projects"},
                ],
                "resources": [
                    {"uri": "linear://issues", "description": "List of issues"},
                    {"uri": "linear://projects", "description": "List of projects"},
                ],
            },
            "github": {
                "name": "GitHub",
                "description": "Manage GitHub repositories and pull requests",
                "tools": [
                    {"name": "create_pr", "description": "Create a pull request"},
                    {"name": "list_prs", "description": "List pull requests"},
                    {"name": "get_pr", "description": "Get PR details"},
                    {"name": "merge_pr", "description": "Merge a pull request"},
                    {"name": "list_issues", "description": "List repository issues"},
                    {"name": "create_issue", "description": "Create an issue"},
                ],
                "resources": [
                    {"uri": "github://repos", "description": "List of repositories"},
                    {"uri": "github://prs", "description": "List of pull requests"},
                ],
            },
            "notion": {
                "name": "Notion",
                "description": "Access and edit Notion documents",
                "tools": [
                    {"name": "get_page", "description": "Get a Notion page"},
                    {"name": "create_page", "description": "Create a new page"},
                    {"name": "update_page", "description": "Update a page"},
                    {"name": "search", "description": "Search Notion"},
                    {"name": "list_databases", "description": "List databases"},
                ],
                "resources": [
                    {"uri": "notion://pages", "description": "List of pages"},
                    {"uri": "notion://databases", "description": "List of databases"},
                ],
            },
            "jira": {
                "name": "Jira",
                "description": "Track Jira issues and sprints",
                "tools": [
                    {"name": "create_issue", "description": "Create a Jira issue"},
                    {"name": "update_issue", "description": "Update an issue"},
                    {"name": "list_issues", "description": "List issues"},
                    {"name": "get_issue", "description": "Get issue details"},
                    {"name": "list_sprints", "description": "List sprints"},
                    {"name": "add_comment", "description": "Add a comment to an issue"},
                ],
                "resources": [
                    {"uri": "jira://issues", "description": "List of issues"},
                    {"uri": "jira://projects", "description": "List of projects"},
                ],
            },
            "confluence": {
                "name": "Confluence",
                "description": "Access Confluence documentation",
                "tools": [
                    {"name": "get_page", "description": "Get a Confluence page"},
                    {"name": "create_page", "description": "Create a new page"},
                    {"name": "update_page", "description": "Update a page"},
                    {"name": "search", "description": "Search Confluence"},
                ],
                "resources": [
                    {"uri": "confluence://pages", "description": "List of pages"},
                    {"uri": "confluence://spaces", "description": "List of spaces"},
                ],
            },
        }

    async def execute(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute an MCP operation."""
        commands = {
            "list_servers": self.list_servers,
            "list_tools": self.list_tools,
            "call_tool": self.call_tool,
            "read_resource": self.read_resource,
            "connect": self.connect_server,
            "disconnect": self.disconnect_server,
        }

        if command not in commands:
            return {"error": f"Unknown command: {command}"}

        return await commands[command](**kwargs)

    async def list_servers(self, **kwargs: Any) -> Dict[str, Any]:
        """List all available MCP servers."""
        servers_list = []
        for server_id, server_info in self.servers.items():
            servers_list.append({
                "id": server_id,
                "name": server_info["name"],
                "description": server_info["description"],
                "connected": server_id in self.connections,
                "tools_count": len(server_info.get("tools", [])),
                "resources_count": len(server_info.get("resources", [])),
            })

        return {
            "success": True,
            "servers": servers_list,
            "count": len(servers_list),
        }

    async def list_tools(
        self,
        server: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List all tools and resources available on an MCP server."""
        if server not in self.servers:
            return {"error": f"Server not found: {server}"}

        server_info = self.servers[server]
        return {
            "success": True,
            "server": server,
            "name": server_info["name"],
            "tools": server_info.get("tools", []),
            "resources": server_info.get("resources", []),
        }

    async def call_tool(
        self,
        server: str,
        tool_name: str,
        tool_args: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a specific tool on an MCP server."""
        if server not in self.servers:
            return {"error": f"Server not found: {server}"}

        server_info = self.servers[server]
        tools = {t["name"]: t for t in server_info.get("tools", [])}

        if tool_name not in tools:
            return {"error": f"Tool not found: {tool_name} on server {server}"}

        # Parse tool arguments
        args = {}
        if tool_args:
            try:
                args = json.loads(tool_args)
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON in tool_args: {tool_args}"}

        # Simulate tool execution (in real implementation, would call actual MCP server)
        return {
            "success": True,
            "server": server,
            "tool": tool_name,
            "args": args,
            "result": {
                "message": f"Tool '{tool_name}' executed successfully on {server}",
                "simulated": True,
                "note": "This is a simulated response. Connect to actual MCP server for real results.",
            },
        }

    async def read_resource(
        self,
        server: str,
        resource_uri: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Read a specific resource from an MCP server."""
        if server not in self.servers:
            return {"error": f"Server not found: {server}"}

        server_info = self.servers[server]
        resources = {r["uri"]: r for r in server_info.get("resources", [])}

        if resource_uri not in resources:
            return {"error": f"Resource not found: {resource_uri} on server {server}"}

        # Simulate resource reading
        return {
            "success": True,
            "server": server,
            "resource_uri": resource_uri,
            "description": resources[resource_uri]["description"],
            "content": {
                "message": f"Resource '{resource_uri}' read successfully",
                "simulated": True,
                "note": "This is a simulated response. Connect to actual MCP server for real data.",
            },
        }

    async def connect_server(
        self,
        server: str,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Connect to an MCP server."""
        if server not in self.servers:
            return {"error": f"Server not found: {server}"}

        if server in self.connections:
            return {
                "success": True,
                "server": server,
                "message": "Already connected",
            }

        # Simulate connection (in real implementation, would establish actual connection)
        self.connections[server] = {
            "connected_at": asyncio.get_event_loop().time(),
            "config": config or {},
        }

        return {
            "success": True,
            "server": server,
            "message": f"Connected to {self.servers[server]['name']}",
        }

    async def disconnect_server(
        self,
        server: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Disconnect from an MCP server."""
        if server not in self.connections:
            return {
                "success": True,
                "server": server,
                "message": "Not connected",
            }

        del self.connections[server]

        return {
            "success": True,
            "server": server,
            "message": f"Disconnected from {self.servers[server]['name']}",
        }

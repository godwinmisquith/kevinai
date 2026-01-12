"""MCP (Model Context Protocol) tool with marketplace for integrating with external services."""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.tools.base import BaseTool


class MCPCategory(str, Enum):
    """Categories for MCP servers."""
    COMMUNICATION = "communication"
    PROJECT_MANAGEMENT = "project_management"
    DEVELOPMENT = "development"
    DOCUMENTATION = "documentation"
    DATABASE = "database"
    CLOUD = "cloud"
    AI_ML = "ai_ml"
    ANALYTICS = "analytics"
    SECURITY = "security"
    OTHER = "other"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    id: str
    name: str
    description: str
    category: MCPCategory
    icon: str
    author: str
    version: str
    tools: List[Dict[str, str]] = field(default_factory=list)
    resources: List[Dict[str, str]] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    requires_auth: bool = False
    auth_type: Optional[str] = None
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    downloads: int = 0
    rating: float = 0.0
    featured: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "icon": self.icon,
            "author": self.author,
            "version": self.version,
            "tools": self.tools,
            "resources": self.resources,
            "config_schema": self.config_schema,
            "requires_auth": self.requires_auth,
            "auth_type": self.auth_type,
            "documentation_url": self.documentation_url,
            "repository_url": self.repository_url,
            "downloads": self.downloads,
            "rating": self.rating,
            "featured": self.featured,
        }


class MCPMarketplace:
    """MCP Server Marketplace registry."""

    def __init__(self):
        self.registry: Dict[str, MCPServerConfig] = {}
        self._populate_registry()

    def _populate_registry(self) -> None:
        """Populate the marketplace with available MCP servers."""
        servers = [
            MCPServerConfig(
                id="slack",
                name="Slack",
                description="Send messages, manage channels, and interact with Slack workspaces",
                category=MCPCategory.COMMUNICATION,
                icon="slack",
                author="Anthropic",
                version="1.2.0",
                tools=[
                    {"name": "send_message", "description": "Send a message to a channel or user"},
                    {"name": "list_channels", "description": "List available channels"},
                    {"name": "get_messages", "description": "Get recent messages from a channel"},
                    {"name": "create_channel", "description": "Create a new channel"},
                    {"name": "upload_file", "description": "Upload a file to a channel"},
                    {"name": "add_reaction", "description": "Add a reaction to a message"},
                ],
                resources=[
                    {"uri": "slack://channels", "description": "List of channels"},
                    {"uri": "slack://users", "description": "List of users"},
                    {"uri": "slack://messages/{channel}", "description": "Messages in a channel"},
                ],
                config_schema={
                    "bot_token": {"type": "string", "required": True, "secret": True},
                    "app_token": {"type": "string", "required": False, "secret": True},
                },
                requires_auth=True,
                auth_type="oauth",
                documentation_url="https://api.slack.com/docs",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/slack",
                downloads=15420,
                rating=4.8,
                featured=True,
            ),
            MCPServerConfig(
                id="github",
                name="GitHub",
                description="Manage repositories, pull requests, issues, and GitHub Actions",
                category=MCPCategory.DEVELOPMENT,
                icon="github",
                author="Anthropic",
                version="1.3.0",
                tools=[
                    {"name": "create_repository", "description": "Create a new repository"},
                    {"name": "create_pr", "description": "Create a pull request"},
                    {"name": "list_prs", "description": "List pull requests"},
                    {"name": "merge_pr", "description": "Merge a pull request"},
                    {"name": "create_issue", "description": "Create an issue"},
                    {"name": "list_issues", "description": "List repository issues"},
                    {"name": "create_branch", "description": "Create a new branch"},
                    {"name": "get_file", "description": "Get file contents"},
                    {"name": "commit_files", "description": "Commit files to a branch"},
                ],
                resources=[
                    {"uri": "github://repos", "description": "List of repositories"},
                    {"uri": "github://repos/{owner}/{repo}", "description": "Repository details"},
                    {"uri": "github://repos/{owner}/{repo}/pulls", "description": "Pull requests"},
                    {"uri": "github://repos/{owner}/{repo}/issues", "description": "Issues"},
                ],
                config_schema={
                    "token": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="token",
                documentation_url="https://docs.github.com/en/rest",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/github",
                downloads=28350,
                rating=4.9,
                featured=True,
            ),
            MCPServerConfig(
                id="linear",
                name="Linear",
                description="Manage issues, projects, and sprints in Linear",
                category=MCPCategory.PROJECT_MANAGEMENT,
                icon="linear",
                author="Anthropic",
                version="1.1.0",
                tools=[
                    {"name": "create_issue", "description": "Create a new issue"},
                    {"name": "update_issue", "description": "Update an existing issue"},
                    {"name": "list_issues", "description": "List issues with filters"},
                    {"name": "get_issue", "description": "Get issue details"},
                    {"name": "list_projects", "description": "List projects"},
                    {"name": "create_project", "description": "Create a new project"},
                    {"name": "list_cycles", "description": "List cycles/sprints"},
                ],
                resources=[
                    {"uri": "linear://issues", "description": "List of issues"},
                    {"uri": "linear://projects", "description": "List of projects"},
                    {"uri": "linear://teams", "description": "List of teams"},
                ],
                config_schema={
                    "api_key": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="api_key",
                documentation_url="https://developers.linear.app/docs",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/linear",
                downloads=12840,
                rating=4.7,
                featured=True,
            ),
            MCPServerConfig(
                id="notion",
                name="Notion",
                description="Access and edit Notion pages, databases, and workspaces",
                category=MCPCategory.DOCUMENTATION,
                icon="notion",
                author="Anthropic",
                version="1.0.2",
                tools=[
                    {"name": "get_page", "description": "Get a Notion page"},
                    {"name": "create_page", "description": "Create a new page"},
                    {"name": "update_page", "description": "Update a page"},
                    {"name": "search", "description": "Search Notion"},
                    {"name": "list_databases", "description": "List databases"},
                    {"name": "query_database", "description": "Query a database"},
                    {"name": "create_database", "description": "Create a database"},
                ],
                resources=[
                    {"uri": "notion://pages", "description": "List of pages"},
                    {"uri": "notion://databases", "description": "List of databases"},
                    {"uri": "notion://pages/{id}", "description": "Page content"},
                ],
                config_schema={
                    "integration_token": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="token",
                documentation_url="https://developers.notion.com/docs",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/notion",
                downloads=18920,
                rating=4.6,
                featured=True,
            ),
            MCPServerConfig(
                id="jira",
                name="Jira",
                description="Track issues, sprints, and projects in Jira",
                category=MCPCategory.PROJECT_MANAGEMENT,
                icon="jira",
                author="Atlassian",
                version="1.0.1",
                tools=[
                    {"name": "create_issue", "description": "Create a Jira issue"},
                    {"name": "update_issue", "description": "Update an issue"},
                    {"name": "list_issues", "description": "List issues with JQL"},
                    {"name": "get_issue", "description": "Get issue details"},
                    {"name": "list_sprints", "description": "List sprints"},
                    {"name": "add_comment", "description": "Add a comment to an issue"},
                    {"name": "transition_issue", "description": "Transition issue status"},
                ],
                resources=[
                    {"uri": "jira://issues", "description": "List of issues"},
                    {"uri": "jira://projects", "description": "List of projects"},
                    {"uri": "jira://boards", "description": "List of boards"},
                ],
                config_schema={
                    "domain": {"type": "string", "required": True},
                    "email": {"type": "string", "required": True},
                    "api_token": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="basic",
                documentation_url="https://developer.atlassian.com/cloud/jira/platform/rest/v3/",
                downloads=9650,
                rating=4.5,
            ),
            MCPServerConfig(
                id="confluence",
                name="Confluence",
                description="Access and edit Confluence documentation and spaces",
                category=MCPCategory.DOCUMENTATION,
                icon="confluence",
                author="Atlassian",
                version="1.0.0",
                tools=[
                    {"name": "get_page", "description": "Get a Confluence page"},
                    {"name": "create_page", "description": "Create a new page"},
                    {"name": "update_page", "description": "Update a page"},
                    {"name": "search", "description": "Search Confluence"},
                    {"name": "list_spaces", "description": "List spaces"},
                ],
                resources=[
                    {"uri": "confluence://pages", "description": "List of pages"},
                    {"uri": "confluence://spaces", "description": "List of spaces"},
                ],
                config_schema={
                    "domain": {"type": "string", "required": True},
                    "email": {"type": "string", "required": True},
                    "api_token": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="basic",
                documentation_url="https://developer.atlassian.com/cloud/confluence/rest/v2/",
                downloads=7230,
                rating=4.4,
            ),
            MCPServerConfig(
                id="postgres",
                name="PostgreSQL",
                description="Query and manage PostgreSQL databases",
                category=MCPCategory.DATABASE,
                icon="database",
                author="Anthropic",
                version="1.0.0",
                tools=[
                    {"name": "query", "description": "Execute a SQL query"},
                    {"name": "list_tables", "description": "List database tables"},
                    {"name": "describe_table", "description": "Get table schema"},
                    {"name": "insert", "description": "Insert data into a table"},
                    {"name": "update", "description": "Update data in a table"},
                ],
                resources=[
                    {"uri": "postgres://tables", "description": "List of tables"},
                    {"uri": "postgres://schema/{table}", "description": "Table schema"},
                ],
                config_schema={
                    "connection_string": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="connection_string",
                documentation_url="https://www.postgresql.org/docs/",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
                downloads=11200,
                rating=4.7,
                featured=True,
            ),
            MCPServerConfig(
                id="sqlite",
                name="SQLite",
                description="Query and manage SQLite databases",
                category=MCPCategory.DATABASE,
                icon="database",
                author="Anthropic",
                version="1.0.0",
                tools=[
                    {"name": "query", "description": "Execute a SQL query"},
                    {"name": "list_tables", "description": "List database tables"},
                    {"name": "describe_table", "description": "Get table schema"},
                ],
                resources=[
                    {"uri": "sqlite://tables", "description": "List of tables"},
                ],
                config_schema={
                    "database_path": {"type": "string", "required": True},
                },
                requires_auth=False,
                documentation_url="https://www.sqlite.org/docs.html",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
                downloads=8450,
                rating=4.6,
            ),
            MCPServerConfig(
                id="filesystem",
                name="Filesystem",
                description="Read and write files on the local filesystem",
                category=MCPCategory.DEVELOPMENT,
                icon="folder",
                author="Anthropic",
                version="1.0.0",
                tools=[
                    {"name": "read_file", "description": "Read a file"},
                    {"name": "write_file", "description": "Write to a file"},
                    {"name": "list_directory", "description": "List directory contents"},
                    {"name": "create_directory", "description": "Create a directory"},
                    {"name": "delete", "description": "Delete a file or directory"},
                    {"name": "move", "description": "Move/rename a file"},
                ],
                resources=[
                    {"uri": "file://{path}", "description": "File contents"},
                ],
                config_schema={
                    "allowed_paths": {"type": "array", "required": True},
                },
                requires_auth=False,
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
                downloads=21300,
                rating=4.8,
            ),
            MCPServerConfig(
                id="brave-search",
                name="Brave Search",
                description="Search the web using Brave Search API",
                category=MCPCategory.OTHER,
                icon="search",
                author="Anthropic",
                version="1.0.0",
                tools=[
                    {"name": "search", "description": "Search the web"},
                    {"name": "news_search", "description": "Search news articles"},
                ],
                resources=[],
                config_schema={
                    "api_key": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="api_key",
                documentation_url="https://brave.com/search/api/",
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
                downloads=6780,
                rating=4.5,
            ),
            MCPServerConfig(
                id="google-drive",
                name="Google Drive",
                description="Access and manage files in Google Drive",
                category=MCPCategory.CLOUD,
                icon="google-drive",
                author="Google",
                version="1.0.0",
                tools=[
                    {"name": "list_files", "description": "List files in Drive"},
                    {"name": "get_file", "description": "Get file contents"},
                    {"name": "upload_file", "description": "Upload a file"},
                    {"name": "create_folder", "description": "Create a folder"},
                    {"name": "share_file", "description": "Share a file"},
                    {"name": "search", "description": "Search files"},
                ],
                resources=[
                    {"uri": "gdrive://files", "description": "List of files"},
                    {"uri": "gdrive://files/{id}", "description": "File contents"},
                ],
                config_schema={
                    "credentials_json": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="oauth",
                documentation_url="https://developers.google.com/drive/api/guides/about-sdk",
                downloads=14500,
                rating=4.6,
            ),
            MCPServerConfig(
                id="aws",
                name="AWS",
                description="Interact with AWS services (S3, Lambda, EC2, etc.)",
                category=MCPCategory.CLOUD,
                icon="aws",
                author="Amazon",
                version="1.0.0",
                tools=[
                    {"name": "s3_list_buckets", "description": "List S3 buckets"},
                    {"name": "s3_get_object", "description": "Get S3 object"},
                    {"name": "s3_put_object", "description": "Put S3 object"},
                    {"name": "lambda_invoke", "description": "Invoke Lambda function"},
                    {"name": "ec2_list_instances", "description": "List EC2 instances"},
                ],
                resources=[
                    {"uri": "aws://s3/buckets", "description": "S3 buckets"},
                    {"uri": "aws://lambda/functions", "description": "Lambda functions"},
                ],
                config_schema={
                    "access_key_id": {"type": "string", "required": True, "secret": True},
                    "secret_access_key": {"type": "string", "required": True, "secret": True},
                    "region": {"type": "string", "required": True},
                },
                requires_auth=True,
                auth_type="aws_credentials",
                documentation_url="https://docs.aws.amazon.com/",
                downloads=9870,
                rating=4.5,
            ),
            MCPServerConfig(
                id="sentry",
                name="Sentry",
                description="Monitor errors and performance with Sentry",
                category=MCPCategory.ANALYTICS,
                icon="sentry",
                author="Sentry",
                version="1.0.0",
                tools=[
                    {"name": "list_issues", "description": "List error issues"},
                    {"name": "get_issue", "description": "Get issue details"},
                    {"name": "resolve_issue", "description": "Resolve an issue"},
                    {"name": "list_projects", "description": "List projects"},
                ],
                resources=[
                    {"uri": "sentry://issues", "description": "List of issues"},
                    {"uri": "sentry://projects", "description": "List of projects"},
                ],
                config_schema={
                    "auth_token": {"type": "string", "required": True, "secret": True},
                    "organization": {"type": "string", "required": True},
                },
                requires_auth=True,
                auth_type="token",
                documentation_url="https://docs.sentry.io/api/",
                downloads=5430,
                rating=4.4,
            ),
            MCPServerConfig(
                id="datadog",
                name="Datadog",
                description="Monitor metrics, logs, and traces with Datadog",
                category=MCPCategory.ANALYTICS,
                icon="datadog",
                author="Datadog",
                version="1.0.0",
                tools=[
                    {"name": "query_metrics", "description": "Query metrics"},
                    {"name": "search_logs", "description": "Search logs"},
                    {"name": "list_monitors", "description": "List monitors"},
                    {"name": "create_monitor", "description": "Create a monitor"},
                ],
                resources=[
                    {"uri": "datadog://metrics", "description": "Available metrics"},
                    {"uri": "datadog://monitors", "description": "List of monitors"},
                ],
                config_schema={
                    "api_key": {"type": "string", "required": True, "secret": True},
                    "app_key": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="api_key",
                documentation_url="https://docs.datadoghq.com/api/",
                downloads=4210,
                rating=4.3,
            ),
            MCPServerConfig(
                id="openai",
                name="OpenAI",
                description="Access OpenAI models and APIs",
                category=MCPCategory.AI_ML,
                icon="openai",
                author="OpenAI",
                version="1.0.0",
                tools=[
                    {"name": "chat_completion", "description": "Generate chat completions"},
                    {"name": "embeddings", "description": "Generate embeddings"},
                    {"name": "image_generation", "description": "Generate images with DALL-E"},
                    {"name": "speech_to_text", "description": "Transcribe audio"},
                ],
                resources=[
                    {"uri": "openai://models", "description": "Available models"},
                ],
                config_schema={
                    "api_key": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="api_key",
                documentation_url="https://platform.openai.com/docs/api-reference",
                downloads=18900,
                rating=4.8,
            ),
            MCPServerConfig(
                id="puppeteer",
                name="Puppeteer",
                description="Browser automation and web scraping",
                category=MCPCategory.DEVELOPMENT,
                icon="chrome",
                author="Anthropic",
                version="1.0.0",
                tools=[
                    {"name": "navigate", "description": "Navigate to a URL"},
                    {"name": "screenshot", "description": "Take a screenshot"},
                    {"name": "click", "description": "Click an element"},
                    {"name": "type", "description": "Type text"},
                    {"name": "evaluate", "description": "Execute JavaScript"},
                ],
                resources=[],
                config_schema={},
                requires_auth=False,
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
                downloads=7650,
                rating=4.5,
            ),
            MCPServerConfig(
                id="memory",
                name="Memory",
                description="Persistent memory storage for conversations",
                category=MCPCategory.AI_ML,
                icon="brain",
                author="Anthropic",
                version="1.0.0",
                tools=[
                    {"name": "store", "description": "Store a memory"},
                    {"name": "retrieve", "description": "Retrieve memories"},
                    {"name": "search", "description": "Search memories"},
                    {"name": "delete", "description": "Delete a memory"},
                ],
                resources=[
                    {"uri": "memory://all", "description": "All stored memories"},
                ],
                config_schema={
                    "storage_path": {"type": "string", "required": False},
                },
                requires_auth=False,
                repository_url="https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
                downloads=12340,
                rating=4.6,
            ),
            MCPServerConfig(
                id="discord",
                name="Discord",
                description="Send messages and manage Discord servers",
                category=MCPCategory.COMMUNICATION,
                icon="discord",
                author="Discord",
                version="1.0.0",
                tools=[
                    {"name": "send_message", "description": "Send a message to a channel"},
                    {"name": "list_channels", "description": "List server channels"},
                    {"name": "list_members", "description": "List server members"},
                    {"name": "create_channel", "description": "Create a channel"},
                ],
                resources=[
                    {"uri": "discord://servers", "description": "List of servers"},
                    {"uri": "discord://channels", "description": "List of channels"},
                ],
                config_schema={
                    "bot_token": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="token",
                documentation_url="https://discord.com/developers/docs",
                downloads=6120,
                rating=4.4,
            ),
            MCPServerConfig(
                id="gitlab",
                name="GitLab",
                description="Manage GitLab repositories, merge requests, and CI/CD",
                category=MCPCategory.DEVELOPMENT,
                icon="gitlab",
                author="GitLab",
                version="1.0.0",
                tools=[
                    {"name": "create_mr", "description": "Create a merge request"},
                    {"name": "list_mrs", "description": "List merge requests"},
                    {"name": "list_pipelines", "description": "List CI/CD pipelines"},
                    {"name": "create_issue", "description": "Create an issue"},
                    {"name": "list_issues", "description": "List issues"},
                ],
                resources=[
                    {"uri": "gitlab://projects", "description": "List of projects"},
                    {"uri": "gitlab://mrs", "description": "Merge requests"},
                ],
                config_schema={
                    "token": {"type": "string", "required": True, "secret": True},
                    "base_url": {"type": "string", "required": False},
                },
                requires_auth=True,
                auth_type="token",
                documentation_url="https://docs.gitlab.com/ee/api/",
                downloads=5890,
                rating=4.5,
            ),
            MCPServerConfig(
                id="vercel",
                name="Vercel",
                description="Deploy and manage Vercel projects",
                category=MCPCategory.CLOUD,
                icon="vercel",
                author="Vercel",
                version="1.0.0",
                tools=[
                    {"name": "list_projects", "description": "List projects"},
                    {"name": "list_deployments", "description": "List deployments"},
                    {"name": "create_deployment", "description": "Create a deployment"},
                    {"name": "get_deployment_logs", "description": "Get deployment logs"},
                ],
                resources=[
                    {"uri": "vercel://projects", "description": "List of projects"},
                    {"uri": "vercel://deployments", "description": "List of deployments"},
                ],
                config_schema={
                    "token": {"type": "string", "required": True, "secret": True},
                },
                requires_auth=True,
                auth_type="token",
                documentation_url="https://vercel.com/docs/rest-api",
                downloads=4560,
                rating=4.4,
            ),
        ]

        for server in servers:
            self.registry[server.id] = server

    def get_all(self) -> List[MCPServerConfig]:
        """Get all servers in the registry."""
        return list(self.registry.values())

    def get_by_id(self, server_id: str) -> Optional[MCPServerConfig]:
        """Get a server by ID."""
        return self.registry.get(server_id)

    def get_by_category(self, category: MCPCategory) -> List[MCPServerConfig]:
        """Get servers by category."""
        return [s for s in self.registry.values() if s.category == category]

    def get_featured(self) -> List[MCPServerConfig]:
        """Get featured servers."""
        return [s for s in self.registry.values() if s.featured]

    def search(self, query: str) -> List[MCPServerConfig]:
        """Search servers by name or description."""
        query_lower = query.lower()
        return [
            s for s in self.registry.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]


class MCPTool(BaseTool):
    """Tool for Model Context Protocol operations with marketplace."""

    name = "mcp"
    description = "Interact with MCP servers for external service integrations"

    def __init__(self):
        self.marketplace = MCPMarketplace()
        self.installed_servers: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Any] = {}

    async def execute(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute an MCP operation."""
        commands = {
            "list_servers": self.list_servers,
            "list_tools": self.list_tools,
            "call_tool": self.call_tool,
            "read_resource": self.read_resource,
            "connect": self.connect_server,
            "disconnect": self.disconnect_server,
            "marketplace_list": self.marketplace_list,
            "marketplace_search": self.marketplace_search,
            "marketplace_get": self.marketplace_get,
            "marketplace_categories": self.marketplace_categories,
            "marketplace_featured": self.marketplace_featured,
            "install": self.install_server,
            "uninstall": self.uninstall_server,
            "configure": self.configure_server,
            "get_config": self.get_server_config,
            "list_installed": self.list_installed,
        }

        if command not in commands:
            return {"error": f"Unknown command: {command}"}

        return await commands[command](**kwargs)

    async def marketplace_list(
        self,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List all servers in the marketplace."""
        if category:
            try:
                cat = MCPCategory(category)
                servers = self.marketplace.get_by_category(cat)
            except ValueError:
                return {"error": f"Invalid category: {category}"}
        else:
            servers = self.marketplace.get_all()

        servers = sorted(servers, key=lambda s: s.downloads, reverse=True)

        start = (page - 1) * per_page
        end = start + per_page
        paginated = servers[start:end]

        return {
            "success": True,
            "servers": [s.to_dict() for s in paginated],
            "total": len(servers),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(servers) + per_page - 1) // per_page,
        }

    async def marketplace_search(
        self,
        query: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Search the marketplace."""
        servers = self.marketplace.search(query)
        return {
            "success": True,
            "servers": [s.to_dict() for s in servers],
            "count": len(servers),
            "query": query,
        }

    async def marketplace_get(
        self,
        server_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get details of a specific server."""
        server = self.marketplace.get_by_id(server_id)
        if not server:
            return {"error": f"Server not found: {server_id}"}

        return {
            "success": True,
            "server": server.to_dict(),
            "installed": server_id in self.installed_servers,
            "connected": server_id in self.connections,
        }

    async def marketplace_categories(self, **kwargs: Any) -> Dict[str, Any]:
        """List all marketplace categories."""
        categories = []
        for cat in MCPCategory:
            servers = self.marketplace.get_by_category(cat)
            categories.append({
                "id": cat.value,
                "name": cat.value.replace("_", " ").title(),
                "count": len(servers),
            })

        return {
            "success": True,
            "categories": categories,
        }

    async def marketplace_featured(self, **kwargs: Any) -> Dict[str, Any]:
        """Get featured servers."""
        servers = self.marketplace.get_featured()
        return {
            "success": True,
            "servers": [s.to_dict() for s in servers],
            "count": len(servers),
        }

    async def install_server(
        self,
        server_id: str,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Install an MCP server from the marketplace."""
        server = self.marketplace.get_by_id(server_id)
        if not server:
            return {"error": f"Server not found in marketplace: {server_id}"}

        if server_id in self.installed_servers:
            return {
                "success": True,
                "server_id": server_id,
                "message": "Server already installed",
                "already_installed": True,
            }

        self.installed_servers[server_id] = {
            "server": server.to_dict(),
            "config": config or {},
            "enabled": True,
        }

        return {
            "success": True,
            "server_id": server_id,
            "name": server.name,
            "message": f"Successfully installed {server.name}",
            "requires_config": server.requires_auth and not config,
        }

    async def uninstall_server(
        self,
        server_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Uninstall an MCP server."""
        if server_id not in self.installed_servers:
            return {"error": f"Server not installed: {server_id}"}

        if server_id in self.connections:
            del self.connections[server_id]

        server_info = self.installed_servers[server_id]
        del self.installed_servers[server_id]

        return {
            "success": True,
            "server_id": server_id,
            "name": server_info["server"]["name"],
            "message": f"Successfully uninstalled {server_info['server']['name']}",
        }

    async def configure_server(
        self,
        server_id: str,
        config: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Configure an installed MCP server."""
        if server_id not in self.installed_servers:
            return {"error": f"Server not installed: {server_id}"}

        self.installed_servers[server_id]["config"].update(config)

        return {
            "success": True,
            "server_id": server_id,
            "message": "Configuration updated",
            "config": {
                k: "***" if "secret" in k or "token" in k or "key" in k or "password" in k else v
                for k, v in self.installed_servers[server_id]["config"].items()
            },
        }

    async def get_server_config(
        self,
        server_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get configuration for an installed server."""
        if server_id not in self.installed_servers:
            return {"error": f"Server not installed: {server_id}"}

        server = self.marketplace.get_by_id(server_id)
        config = self.installed_servers[server_id]["config"]

        masked_config = {
            k: "***" if "secret" in k or "token" in k or "key" in k or "password" in k else v
            for k, v in config.items()
        }

        return {
            "success": True,
            "server_id": server_id,
            "config": masked_config,
            "config_schema": server.config_schema if server else {},
            "enabled": self.installed_servers[server_id].get("enabled", True),
        }

    async def list_installed(self, **kwargs: Any) -> Dict[str, Any]:
        """List all installed MCP servers."""
        installed = []
        for server_id, info in self.installed_servers.items():
            installed.append({
                "id": server_id,
                "name": info["server"]["name"],
                "description": info["server"]["description"],
                "category": info["server"]["category"],
                "enabled": info.get("enabled", True),
                "connected": server_id in self.connections,
                "configured": bool(info.get("config")),
            })

        return {
            "success": True,
            "servers": installed,
            "count": len(installed),
        }

    async def list_servers(self, **kwargs: Any) -> Dict[str, Any]:
        """List all installed MCP servers (for backward compatibility)."""
        return await self.list_installed(**kwargs)

    async def list_tools(
        self,
        server: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List all tools and resources available on an MCP server."""
        server_config = self.marketplace.get_by_id(server)
        if not server_config:
            return {"error": f"Server not found: {server}"}

        return {
            "success": True,
            "server": server,
            "name": server_config.name,
            "tools": server_config.tools,
            "resources": server_config.resources,
            "installed": server in self.installed_servers,
        }

    async def call_tool(
        self,
        server: str,
        tool_name: str,
        tool_args: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a specific tool on an MCP server."""
        if server not in self.installed_servers:
            return {"error": f"Server not installed: {server}. Install it first using the marketplace."}

        server_config = self.marketplace.get_by_id(server)
        if not server_config:
            return {"error": f"Server not found: {server}"}

        tools = {t["name"]: t for t in server_config.tools}
        if tool_name not in tools:
            return {"error": f"Tool not found: {tool_name} on server {server}"}

        args = {}
        if tool_args:
            try:
                args = json.loads(tool_args)
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON in tool_args: {tool_args}"}

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
        if server not in self.installed_servers:
            return {"error": f"Server not installed: {server}. Install it first using the marketplace."}

        server_config = self.marketplace.get_by_id(server)
        if not server_config:
            return {"error": f"Server not found: {server}"}

        return {
            "success": True,
            "server": server,
            "resource_uri": resource_uri,
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
        if server not in self.installed_servers:
            return {"error": f"Server not installed: {server}. Install it first using the marketplace."}

        if server in self.connections:
            return {
                "success": True,
                "server": server,
                "message": "Already connected",
            }

        self.connections[server] = {
            "connected_at": asyncio.get_event_loop().time(),
            "config": config or self.installed_servers[server].get("config", {}),
        }

        server_config = self.marketplace.get_by_id(server)
        name = server_config.name if server_config else server

        return {
            "success": True,
            "server": server,
            "message": f"Connected to {name}",
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

        server_config = self.marketplace.get_by_id(server)
        name = server_config.name if server_config else server

        return {
            "success": True,
            "server": server,
            "message": f"Disconnected from {name}",
        }

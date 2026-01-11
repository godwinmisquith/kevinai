# Kevin AI - Virtual AI Software Engineer

Kevin AI is a virtual AI software engineer similar to Devin, designed to help developers with coding tasks, file management, shell commands, browser automation, and more.

## Features

Kevin AI includes all the core features of an AI software engineer:

### Code Understanding & Navigation
- **File Explorer**: Browse and view files in your workspace
- **Code Search**: Search files using glob patterns and grep
- **LSP Integration**: Go to definition, find references, hover for documentation

### Code Editing
- **File Operations**: Read, write, and edit files with precise string replacements
- **Code Generation**: AI-powered code generation and completion

### Shell/Terminal Access
- **Command Execution**: Run bash commands with timeout support
- **Background Processes**: Run long-running commands in the background
- **Multiple Sessions**: Support for multiple shell sessions

### Browser Automation
- **Navigation**: Navigate to URLs and take screenshots
- **Interactions**: Click, type, scroll, and interact with web pages
- **Console Access**: Execute JavaScript in the browser console

### Git/Version Control
- **Repository Management**: Clone, status, diff, branch operations
- **Commits**: Stage and commit changes
- **Pull Requests**: Create and manage PRs (requires GitHub integration)

### Task Management
- **Todo List**: Track tasks with pending, in_progress, and completed states
- **Progress Tracking**: Visual progress indicators

### Web Search
- **Search**: Search the web for documentation and information
- **Content Fetching**: Fetch and parse web page content

### AI/LLM Integration
- **OpenAI Support**: GPT-4 and other OpenAI models
- **Anthropic Support**: Claude models
- **Tool Orchestration**: Automatic tool selection and execution

## Architecture

```
kevinai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   │   ├── agent.py    # Agent orchestration
│   │   │   ├── llm.py      # LLM integration
│   │   │   └── session.py  # Session management
│   │   ├── tools/          # Tool implementations
│   │   │   ├── bash.py     # Shell execution
│   │   │   ├── browser.py  # Browser automation
│   │   │   ├── file_ops.py # File operations
│   │   │   ├── git.py      # Git operations
│   │   │   ├── search.py   # Grep/glob search
│   │   │   ├── task.py     # Todo management
│   │   │   └── web.py      # Web search
│   │   ├── config.py       # Configuration
│   │   └── main.py         # FastAPI app
│   └── pyproject.toml      # Python dependencies
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   │   ├── ChatPanel.tsx
    │   │   ├── FileExplorer.tsx
    │   │   ├── Terminal.tsx
    │   │   ├── BrowserPreview.tsx
    │   │   ├── TodoPanel.tsx
    │   │   └── ...
    │   ├── hooks/          # Custom hooks
    │   ├── services/       # API services
    │   └── types/          # TypeScript types
    └── package.json        # Node dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Poetry (for Python dependency management)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Add your API keys to `.env`:
   ```
   OPENAI_API_KEY=your-openai-api-key
   # or
   ANTHROPIC_API_KEY=your-anthropic-api-key
   ```

5. Start the backend server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

The backend will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`.

## API Endpoints

### Sessions
- `POST /api/sessions` - Create a new session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete a session

### Chat
- `POST /api/sessions/{id}/chat` - Send a message
- `GET /api/sessions/{id}/messages` - Get message history

### Todos
- `GET /api/sessions/{id}/todos` - Get todos
- `PUT /api/sessions/{id}/todos` - Update todos

### Tools
- `POST /api/sessions/{id}/tools/execute` - Execute a tool directly

### WebSocket
- `WS /api/ws/{session_id}` - Real-time communication

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `DEFAULT_MODEL` | Default LLM model | `gpt-4-turbo-preview` |
| `MAX_TOKENS` | Max tokens for LLM | `4096` |
| `TEMPERATURE` | LLM temperature | `0.7` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `true` |
| `WORKSPACE_DIR` | Workspace directory | `/tmp/kevin-workspace` |
| `BROWSER_HEADLESS` | Headless browser | `true` |

## Available Tools

Kevin AI has access to the following tools:

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands |
| `read_file` | Read file contents |
| `write_file` | Write content to files |
| `edit_file` | Edit files with string replacement |
| `glob` | Find files by pattern |
| `grep` | Search file contents |
| `browser_navigate` | Navigate browser to URL |
| `browser_click` | Click elements |
| `browser_type` | Type text |
| `browser_screenshot` | Take screenshots |
| `git_status` | Get git status |
| `git_commit` | Commit changes |
| `git_push` | Push to remote |
| `git_create_pr` | Create pull request |
| `web_search` | Search the web |
| `web_get_contents` | Fetch web content |
| `todo_write` | Update task list |
| `message_user` | Send messages |
| `think` | Record thoughts |

## Development

### Running Tests

```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm test
```

### Linting

```bash
# Backend
cd backend
poetry run ruff check .
poetry run black --check .

# Frontend
cd frontend
npm run lint
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by [Devin](https://devin.ai) by Cognition AI
- Built with FastAPI, React, and modern AI technologies

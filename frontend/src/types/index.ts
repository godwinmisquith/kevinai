export interface Session {
  id: string;
  name: string;
  workspace_path?: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  todos: Todo[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  tool_calls?: ToolCall[];
  created_at: string;
}

export interface ToolCall {
  id: string;
  type: string;
  function: {
    name: string;
    arguments: string;
  };
}

export interface Todo {
  id: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface FileEntry {
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: number;
  children?: FileEntry[];
}

export interface ToolResult {
  tool: string;
  args: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  tool_results: ToolResult[];
  iterations: number;
}

export interface ApiError {
  detail: string;
}

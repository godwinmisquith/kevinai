import type { Session, Message, Todo, ChatResponse, FileEntry } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}/api`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  // Session endpoints
  async createSession(name?: string, workspacePath?: string): Promise<Session> {
    return this.request<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify({ name, workspace_path: workspacePath }),
    });
  }

  async listSessions(): Promise<Session[]> {
    return this.request<Session[]>('/sessions');
  }

  async getSession(sessionId: string): Promise<Session> {
    return this.request<Session>(`/sessions/${sessionId}`);
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.request(`/sessions/${sessionId}`, { method: 'DELETE' });
  }

  // Chat endpoints
  async sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
    return this.request<ChatResponse>(`/sessions/${sessionId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async getMessages(sessionId: string): Promise<Message[]> {
    return this.request<Message[]>(`/sessions/${sessionId}/messages`);
  }

  // Todo endpoints
  async getTodos(sessionId: string): Promise<Todo[]> {
    return this.request<Todo[]>(`/sessions/${sessionId}/todos`);
  }

  async updateTodos(sessionId: string, todos: Partial<Todo>[]): Promise<Todo[]> {
    return this.request<Todo[]>(`/sessions/${sessionId}/todos`, {
      method: 'PUT',
      body: JSON.stringify({ todos }),
    });
  }

  // Tool execution
  async executeTool(
    sessionId: string,
    toolName: string,
    args: Record<string, unknown>
  ): Promise<Record<string, unknown>> {
    return this.request(`/sessions/${sessionId}/tools/execute`, {
      method: 'POST',
      body: JSON.stringify({ tool_name: toolName, args }),
    });
  }

  // File operations (via tool execution)
  async readFile(sessionId: string, filePath: string): Promise<{ content: string }> {
    return this.executeTool(sessionId, 'read_file', { file_path: filePath }) as Promise<{ content: string }>;
  }

  async listDirectory(sessionId: string, path: string): Promise<{ entries: FileEntry[] }> {
    return this.executeTool(sessionId, 'read_file', { file_path: path }) as Promise<{ entries: FileEntry[] }>;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }
}

export const api = new ApiService();

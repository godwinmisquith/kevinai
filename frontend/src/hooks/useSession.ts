import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { wsService } from '../services/websocket';
import type { Session, Message, Todo, ChatResponse } from '../types';

export function useSession(sessionId: string | null) {
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Load session data
  useEffect(() => {
    if (!sessionId) return;

    const loadSession = async () => {
      try {
        setLoading(true);
        const data = await api.getSession(sessionId);
        setSession(data);
        setMessages(data.messages);
        setTodos(data.todos);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load session');
      } finally {
        setLoading(false);
      }
    };

    loadSession();
  }, [sessionId]);

  // WebSocket connection
  useEffect(() => {
    if (!sessionId) return;

    wsService.connect(sessionId);

    const handleConnected = () => setIsConnected(true);
    const handleDisconnected = () => setIsConnected(false);
    const handleResponse = (data: unknown) => {
      const response = data as { data: ChatResponse };
      if (response.data?.message) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: response.data.message,
            created_at: new Date().toISOString(),
          },
        ]);
      }
    };

    wsService.on('connected', handleConnected);
    wsService.on('disconnected', handleDisconnected);
    wsService.on('response', handleResponse);

    return () => {
      wsService.off('connected', handleConnected);
      wsService.off('disconnected', handleDisconnected);
      wsService.off('response', handleResponse);
      wsService.disconnect();
    };
  }, [sessionId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId) return;

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        setLoading(true);
        const response = await api.sendMessage(sessionId, content);

        // Add assistant response
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.message,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Refresh todos
        const updatedTodos = await api.getTodos(sessionId);
        setTodos(updatedTodos);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to send message');
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const updateTodos = useCallback(
    async (newTodos: Partial<Todo>[]) => {
      if (!sessionId) return;

      try {
        const updated = await api.updateTodos(sessionId, newTodos);
        setTodos(updated);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to update todos');
      }
    },
    [sessionId]
  );

  return {
    session,
    messages,
    todos,
    loading,
    error,
    isConnected,
    sendMessage,
    updateTodos,
  };
}

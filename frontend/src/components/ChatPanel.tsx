import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, User, Bot, Wrench } from 'lucide-react';
import type { Message } from '../types';

interface ChatPanelProps {
  messages: Message[];
  loading: boolean;
  error: string | null;
  onSendMessage: (message: string) => void;
}

export function ChatPanel({ messages, loading, error, onSendMessage }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const renderMessageContent = (content: string) => {
    // Simple markdown-like rendering
    const parts = content.split(/(```[\s\S]*?```)/g);
    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        const code = part.slice(3, -3);
        const [lang, ...lines] = code.split('\n');
        return (
          <pre key={index} className="bg-kevin-bg rounded-lg p-3 my-2 overflow-x-auto">
            <code className="text-sm">{lines.join('\n') || lang}</code>
          </pre>
        );
      }
      return (
        <span key={index} className="whitespace-pre-wrap">
          {part}
        </span>
      );
    });
  };

  const getMessageIcon = (role: string) => {
    switch (role) {
      case 'user':
        return <User className="w-5 h-5" />;
      case 'assistant':
        return <Bot className="w-5 h-5" />;
      case 'tool':
        return <Wrench className="w-5 h-5" />;
      default:
        return <Bot className="w-5 h-5" />;
    }
  };

  const getMessageStyle = (role: string) => {
    switch (role) {
      case 'user':
        return 'bg-kevin-primary';
      case 'assistant':
        return 'bg-kevin-surface';
      case 'tool':
        return 'bg-kevin-bg border border-kevin-primary';
      default:
        return 'bg-kevin-surface';
    }
  };

  return (
    <div className="h-full flex flex-col bg-kevin-bg">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-kevin-muted">
            <Bot className="w-16 h-16 mb-4 text-kevin-accent" />
            <h2 className="text-xl font-semibold mb-2">Welcome to Kevin AI</h2>
            <p className="text-center max-w-md">
              I'm your virtual AI software engineer. I can help you with coding tasks,
              file management, running commands, and more. How can I help you today?
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' ? 'bg-kevin-accent' : 'bg-kevin-primary'
                }`}
              >
                {getMessageIcon(message.role)}
              </div>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${getMessageStyle(message.role)}`}
              >
                <div className="text-sm">{renderMessageContent(message.content)}</div>
                {message.tool_calls && message.tool_calls.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-kevin-primary">
                    <p className="text-xs text-kevin-muted mb-1">Tool calls:</p>
                    {message.tool_calls.map((tc, idx) => (
                      <div key={idx} className="text-xs bg-kevin-bg rounded px-2 py-1 mt-1">
                        <span className="text-kevin-accent">{tc.function.name}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="text-xs text-kevin-muted mt-2">
                  {new Date(message.created_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-kevin-primary flex items-center justify-center">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
            <div className="bg-kevin-surface rounded-lg px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-kevin-muted">
                <span>Kevin is thinking...</span>
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="bg-red-900 bg-opacity-30 border border-red-500 rounded-lg px-4 py-3 text-red-400 text-sm">
            {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-kevin-primary">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Kevin anything..."
            className="flex-1 bg-kevin-surface border border-kevin-primary rounded-lg px-4 py-3 text-sm resize-none focus:outline-none focus:border-kevin-accent transition-colors"
            rows={2}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 bg-kevin-accent text-white rounded-lg hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-kevin-muted mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}

import { Bot, ChevronDown } from 'lucide-react';

interface AppHeaderProps {
  userName?: string;
  agentMode: 'agent' | 'ask';
  onAgentModeChange: (mode: 'agent' | 'ask') => void;
  isConnected: boolean;
}

export function AppHeader({
  userName = 'Kevin AI',
  agentMode,
  onAgentModeChange,
  isConnected,
}: AppHeaderProps) {
  return (
    <header className="h-12 bg-kevin-bg border-b border-kevin-primary flex items-center justify-between px-4">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-kevin-accent" />
          <span className="font-semibold text-kevin-text">{userName}</span>
        </div>
        <ChevronDown className="w-4 h-4 text-kevin-muted" />
      </div>

      <div className="flex items-center gap-2">
        <div className="flex bg-kevin-surface rounded-full p-1">
          <button
            onClick={() => onAgentModeChange('agent')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              agentMode === 'agent'
                ? 'bg-kevin-primary text-kevin-text'
                : 'text-kevin-muted hover:text-kevin-text'
            }`}
          >
            <Bot className="w-4 h-4" />
            Agent
          </button>
          <button
            onClick={() => onAgentModeChange('ask')}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              agentMode === 'ask'
                ? 'bg-kevin-primary text-kevin-text'
                : 'text-kevin-muted hover:text-kevin-text'
            }`}
          >
            Ask
          </button>
        </div>

        <div className="ml-4 flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-xs text-kevin-muted">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </header>
  );
}

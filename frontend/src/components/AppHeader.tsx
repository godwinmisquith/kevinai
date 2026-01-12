import { Bot, ChevronDown, Settings, Puzzle, BookOpen } from 'lucide-react';

interface AppHeaderProps {
  userName?: string;
  agentMode: 'agent' | 'ask';
  onAgentModeChange: (mode: 'agent' | 'ask') => void;
  isConnected: boolean;
  onOpenMCPMarketplace?: () => void;
  onOpenKnowledge?: () => void;
}

export function AppHeader({
  userName = 'Kevin AI',
  agentMode,
  onAgentModeChange,
  isConnected,
  onOpenMCPMarketplace,
  onOpenKnowledge,
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

        <div className="ml-4 flex items-center gap-4">
          {onOpenKnowledge && (
            <button
              onClick={onOpenKnowledge}
              className="flex items-center gap-2 px-3 py-1.5 bg-kevin-surface rounded-lg text-sm text-kevin-muted hover:text-kevin-text hover:bg-kevin-primary transition-colors"
              title="Knowledge"
            >
              <BookOpen className="w-4 h-4" />
              <span>Knowledge</span>
            </button>
          )}

          {onOpenMCPMarketplace && (
            <button
              onClick={onOpenMCPMarketplace}
              className="flex items-center gap-2 px-3 py-1.5 bg-kevin-surface rounded-lg text-sm text-kevin-muted hover:text-kevin-text hover:bg-kevin-primary transition-colors"
              title="MCP Marketplace"
            >
              <Puzzle className="w-4 h-4" />
              <span>MCPs</span>
            </button>
          )}

          <button
            className="p-2 text-kevin-muted hover:text-kevin-text transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-2">
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
      </div>
    </header>
  );
}

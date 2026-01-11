import { useState } from 'react';
import {
  Send,
  Paperclip,
  AtSign,
  ChevronDown,
  X,
  Sparkles,
  AlertTriangle,
  Bot,
} from 'lucide-react';

interface LandingPageProps {
  onSendMessage: (message: string) => void;
  onStartSession: () => void;
  agentMode: 'agent' | 'ask';
  onAgentModeChange: (mode: 'agent' | 'ask') => void;
  selectedMCPs: string[];
  onMCPsChange: (mcps: string[]) => void;
}

export function LandingPage({
  onSendMessage,
  onStartSession,
  _agentMode,
  _onAgentModeChange,
  selectedMCPs,
  onMCPsChange,
}: LandingPageProps) {
  const [message, setMessage] = useState('');
  const [showRepoSetupBanner, setShowRepoSetupBanner] = useState(true);
  const [showDataAnalystBanner, setShowDataAnalystBanner] = useState(true);
  const [showMCPDropdown, setShowMCPDropdown] = useState(false);
  const [showAgentDropdown, setShowAgentDropdown] = useState(false);

  const availableMCPs = [
    { id: 'slack', name: 'Slack', description: 'Send messages and manage channels' },
    { id: 'linear', name: 'Linear', description: 'Manage issues and projects' },
    { id: 'github', name: 'GitHub', description: 'Manage repositories and PRs' },
    { id: 'notion', name: 'Notion', description: 'Access and edit documents' },
    { id: 'jira', name: 'Jira', description: 'Track issues and sprints' },
  ];

  const agentTypes = [
    { id: 'software-engineer', name: 'Software Engineer', description: 'Build features, fix bugs, work on code' },
    { id: 'data-analyst', name: 'Data Analyst', description: 'Query data sources and discover insights' },
  ];

  const [selectedAgent, setSelectedAgent] = useState(agentTypes[0]);

  const handleSubmit = () => {
    if (message.trim()) {
      onStartSession();
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleMCP = (mcpId: string) => {
    if (selectedMCPs.includes(mcpId)) {
      onMCPsChange(selectedMCPs.filter((id) => id !== mcpId));
    } else {
      onMCPsChange([...selectedMCPs, mcpId]);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-8 py-12">
      <div className="w-full max-w-3xl">
        <h1 className="text-4xl font-semibold text-center mb-12 text-kevin-text">
          What do you want to get done?
        </h1>

        {showRepoSetupBanner && (
          <div className="mb-4 bg-kevin-surface border border-kevin-primary rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              <span className="text-kevin-text">
                Save up to 10 minutes per session by setting up your repository.
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 bg-kevin-primary hover:bg-kevin-accent text-kevin-text rounded text-sm transition-colors">
                Set up repo
              </button>
              <button
                onClick={() => setShowRepoSetupBanner(false)}
                className="p-1 hover:bg-kevin-primary rounded transition-colors"
              >
                <X className="w-4 h-4 text-kevin-muted" />
              </button>
            </div>
          </div>
        )}

        {showDataAnalystBanner && (
          <div className="mb-8 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/30 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-purple-400" />
              <span className="text-kevin-text">
                Try the new{' '}
                <button className="text-purple-400 underline hover:text-purple-300">
                  Data Analyst Agent
                </button>{' '}
                on the agent dropdown below for querying your data sources and discovering business insights.
              </span>
            </div>
            <button
              onClick={() => setShowDataAnalystBanner(false)}
              className="p-1 hover:bg-kevin-primary rounded transition-colors"
            >
              <X className="w-4 h-4 text-kevin-muted" />
            </button>
          </div>
        )}

        <div className="bg-kevin-surface border border-kevin-primary rounded-xl overflow-hidden">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Kevin to build features, fix bugs, or work on your code..."
            className="w-full bg-transparent text-kevin-text placeholder-kevin-muted p-4 resize-none focus:outline-none min-h-32"
            rows={4}
          />

          <div className="flex items-center justify-between px-4 py-3 border-t border-kevin-primary">
            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text">
                <AtSign className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text">
                <Paperclip className="w-5 h-5" />
              </button>

              <div className="h-6 w-px bg-kevin-primary mx-1" />

              <div className="relative">
                <button
                  onClick={() => setShowMCPDropdown(!showMCPDropdown)}
                  className="flex items-center gap-1 px-3 py-1.5 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text text-sm"
                >
                  <span>{selectedMCPs.length} MCPs</span>
                  <ChevronDown className="w-4 h-4" />
                </button>

                {showMCPDropdown && (
                  <div className="absolute bottom-full left-0 mb-2 w-64 bg-kevin-surface border border-kevin-primary rounded-lg shadow-xl z-50">
                    <div className="p-2">
                      <div className="text-xs text-kevin-muted uppercase tracking-wide px-2 py-1">
                        Available MCPs
                      </div>
                      {availableMCPs.map((mcp) => (
                        <button
                          key={mcp.id}
                          onClick={() => toggleMCP(mcp.id)}
                          className={`w-full flex items-center gap-3 px-2 py-2 rounded-lg transition-colors ${
                            selectedMCPs.includes(mcp.id)
                              ? 'bg-kevin-accent/20 text-kevin-text'
                              : 'hover:bg-kevin-primary text-kevin-muted'
                          }`}
                        >
                          <div
                            className={`w-4 h-4 rounded border ${
                              selectedMCPs.includes(mcp.id)
                                ? 'bg-kevin-accent border-kevin-accent'
                                : 'border-kevin-muted'
                            }`}
                          />
                          <div className="text-left">
                            <div className="text-sm font-medium">{mcp.name}</div>
                            <div className="text-xs text-kevin-muted">{mcp.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="relative">
                <button
                  onClick={() => setShowAgentDropdown(!showAgentDropdown)}
                  className="flex items-center gap-1 px-3 py-1.5 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text text-sm"
                >
                  <span>{selectedAgent.name}</span>
                  <ChevronDown className="w-4 h-4" />
                </button>

                {showAgentDropdown && (
                  <div className="absolute bottom-full left-0 mb-2 w-72 bg-kevin-surface border border-kevin-primary rounded-lg shadow-xl z-50">
                    <div className="p-2">
                      <div className="text-xs text-kevin-muted uppercase tracking-wide px-2 py-1">
                        Select Agent
                      </div>
                      {agentTypes.map((agent) => (
                        <button
                          key={agent.id}
                          onClick={() => {
                            setSelectedAgent(agent);
                            setShowAgentDropdown(false);
                          }}
                          className={`w-full flex items-center gap-3 px-2 py-2 rounded-lg transition-colors ${
                            selectedAgent.id === agent.id
                              ? 'bg-kevin-accent/20 text-kevin-text'
                              : 'hover:bg-kevin-primary text-kevin-muted'
                          }`}
                        >
                          {agent.id === 'software-engineer' ? (
                            <Bot className="w-5 h-5" />
                          ) : (
                            <Sparkles className="w-5 h-5" />
                          )}
                          <div className="text-left">
                            <div className="text-sm font-medium">{agent.name}</div>
                            <div className="text-xs text-kevin-muted">{agent.description}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={!message.trim()}
              className={`p-2 rounded-full transition-colors ${
                message.trim()
                  ? 'bg-kevin-accent text-white hover:bg-kevin-accent/80'
                  : 'bg-kevin-primary text-kevin-muted cursor-not-allowed'
              }`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

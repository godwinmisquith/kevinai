import { useState } from 'react';
import {
  Plus,
  List,
  Search,
  Settings,
  HelpCircle,
  ChevronDown,
  ChevronRight,
  GitMerge,
  Clock,
  Loader2,
  XCircle,
  CheckCircle2,
  Folder,
  Bot,
} from 'lucide-react';
import type { Session } from '../types';

interface SessionSidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onCreateSession: () => void;
  onDeleteSession: (sessionId: string) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

function getTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} min`;
  if (diffHours < 24) return `${diffHours} hr`;
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days`;
  return date.toLocaleDateString();
}

function getStatusBadge(status?: string) {
  switch (status) {
    case 'merged':
      return (
        <span className="flex items-center gap-1 text-xs text-green-400">
          <GitMerge className="w-3 h-3" />
          merged
        </span>
      );
    case 'running':
      return (
        <span className="flex items-center gap-1 text-xs text-blue-400">
          <Loader2 className="w-3 h-3 animate-spin" />
          running
        </span>
      );
    case 'completed':
      return (
        <span className="flex items-center gap-1 text-xs text-green-400">
          <CheckCircle2 className="w-3 h-3" />
          completed
        </span>
      );
    case 'failed':
      return (
        <span className="flex items-center gap-1 text-xs text-red-400">
          <XCircle className="w-3 h-3" />
          failed
        </span>
      );
    case 'pending':
      return (
        <span className="flex items-center gap-1 text-xs text-yellow-400">
          <Clock className="w-3 h-3" />
          pending
        </span>
      );
    default:
      return null;
  }
}

export function SessionSidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onCreateSession,
  _onDeleteSession,
  collapsed = false,
}: SessionSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedWorkspaces, setExpandedWorkspaces] = useState<Set<string>>(new Set(['default']));

  const filteredSessions = sessions.filter((session) =>
    session.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groupedSessions = filteredSessions.reduce(
    (acc, session) => {
      const workspace = session.metadata?.workspace || 'default';
      if (!acc[workspace]) {
        acc[workspace] = [];
      }
      acc[workspace].push(session);
      return acc;
    },
    {} as Record<string, Session[]>
  );

  const toggleWorkspace = (workspace: string) => {
    const newExpanded = new Set(expandedWorkspaces);
    if (newExpanded.has(workspace)) {
      newExpanded.delete(workspace);
    } else {
      newExpanded.add(workspace);
    }
    setExpandedWorkspaces(newExpanded);
  };

  if (collapsed) {
    return (
      <div className="w-14 bg-kevin-bg border-r border-kevin-primary flex flex-col items-center py-4 gap-4">
        <button
          onClick={onCreateSession}
          className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text"
          title="New session"
        >
          <Plus className="w-5 h-5" />
        </button>
        <button
          className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text"
          title="All sessions"
        >
          <List className="w-5 h-5" />
        </button>
        <button
          className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text"
          title="Search"
        >
          <Search className="w-5 h-5" />
        </button>
        <div className="flex-1" />
        <button
          className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
        <button
          className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text"
          title="Help"
        >
          <HelpCircle className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-80 bg-kevin-bg border-r border-kevin-primary flex flex-col">
      <div className="p-3 border-b border-kevin-primary">
        <button
          onClick={onCreateSession}
          className="w-full flex items-center gap-2 px-3 py-2 text-kevin-muted hover:text-kevin-text hover:bg-kevin-primary rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span className="text-sm">New session</span>
        </button>
      </div>

      <div className="p-3 border-b border-kevin-primary">
        <button className="w-full flex items-center gap-2 px-3 py-2 text-kevin-muted hover:text-kevin-text hover:bg-kevin-primary rounded-lg transition-colors">
          <List className="w-4 h-4" />
          <span className="text-sm">All sessions</span>
        </button>
      </div>

      <div className="p-3 border-b border-kevin-primary">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-kevin-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search..."
            className="w-full bg-kevin-surface border border-kevin-primary rounded-lg pl-9 pr-3 py-2 text-sm text-kevin-text placeholder-kevin-muted focus:outline-none focus:border-kevin-accent"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {Object.entries(groupedSessions).map(([workspace, workspaceSessions]) => (
          <div key={workspace} className="border-b border-kevin-primary">
            <button
              onClick={() => toggleWorkspace(workspace)}
              className="w-full flex items-center gap-2 px-4 py-2 text-kevin-muted hover:text-kevin-text hover:bg-kevin-primary transition-colors"
            >
              {expandedWorkspaces.has(workspace) ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
              <Folder className="w-4 h-4" />
              <span className="text-sm font-medium">{workspace}</span>
              <span className="text-xs text-kevin-muted ml-auto">
                {workspaceSessions.length}
              </span>
            </button>

            {expandedWorkspaces.has(workspace) && (
              <div className="pb-2">
                {workspaceSessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => onSelectSession(session.id)}
                    className={`w-full flex items-start gap-3 px-4 py-2 transition-colors ${
                      currentSessionId === session.id
                        ? 'bg-kevin-primary/50'
                        : 'hover:bg-kevin-primary/30'
                    }`}
                  >
                    <div className="mt-1">
                      <Bot className="w-5 h-5 text-kevin-accent" />
                    </div>
                    <div className="flex-1 text-left min-w-0">
                      <div className="text-sm text-kevin-text truncate">
                        {session.name}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-kevin-muted">
                          {getTimeAgo(session.created_at)}
                        </span>
                        {getStatusBadge(session.metadata?.status)}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {filteredSessions.length === 0 && (
          <div className="p-4 text-center text-kevin-muted text-sm">
            {searchQuery ? 'No sessions found' : 'No sessions yet'}
          </div>
        )}
      </div>

      <div className="border-t border-kevin-primary p-3">
        <div className="flex items-center justify-between">
          <button className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text">
            <Settings className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-kevin-primary rounded-lg transition-colors text-kevin-muted hover:text-kevin-text">
            <HelpCircle className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

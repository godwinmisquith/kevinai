import { Plus, Trash2, MessageSquare } from 'lucide-react';
import type { Session } from '../types';

interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onDeleteSession: (id: string) => void;
}

export function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
}: SidebarProps) {
  return (
    <aside className="w-64 bg-kevin-surface border-r border-kevin-primary flex flex-col">
      <div className="p-4 border-b border-kevin-primary">
        <button
          onClick={onCreateSession}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-kevin-accent text-white rounded-lg hover:bg-opacity-90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Session
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <h3 className="text-xs font-semibold text-kevin-muted uppercase tracking-wider px-2 py-2">
          Sessions
        </h3>
        {sessions.length === 0 ? (
          <p className="text-sm text-kevin-muted px-2 py-4 text-center">
            No sessions yet. Create one to get started!
          </p>
        ) : (
          <ul className="space-y-1">
            {sessions.map((session) => (
              <li key={session.id}>
                <button
                  onClick={() => onSelectSession(session.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-colors group ${
                    currentSessionId === session.id
                      ? 'bg-kevin-primary text-kevin-text'
                      : 'text-kevin-muted hover:bg-kevin-primary hover:bg-opacity-50'
                  }`}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <span className="flex-1 truncate text-sm">{session.name}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-kevin-accent transition-all"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="p-4 border-t border-kevin-primary">
        <div className="text-xs text-kevin-muted">
          <p>Kevin AI v0.1.0</p>
          <p className="mt-1">Virtual AI Software Engineer</p>
        </div>
      </div>
    </aside>
  );
}

import { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { FileExplorer } from './FileExplorer';
import { Terminal } from './Terminal';
import { BrowserPreview } from './BrowserPreview';
import { TodoPanel } from './TodoPanel';
import { ChatPanel } from './ChatPanel';
import {
  FolderOpen,
  Terminal as TerminalIcon,
  Globe,
  Code,
  Database,
  Eye,
} from 'lucide-react';
import type { Message, Todo } from '../types';

interface WorkspaceViewProps {
  sessionId: string | null;
  messages: Message[];
  todos: Todo[];
  loading: boolean;
  error: string | null;
  onSendMessage: (message: string) => void;
  onUpdateTodos: (todos: Todo[]) => void;
}

type RightPanelTab = 'files' | 'terminal' | 'browser' | 'code' | 'data';

export function WorkspaceView({
  sessionId,
  messages,
  todos,
  loading,
  error,
  onSendMessage,
  onUpdateTodos,
}: WorkspaceViewProps) {
  const [activeRightPanel, setActiveRightPanel] = useState<RightPanelTab>('files');
  const [showPreview, setShowPreview] = useState(false);

  const rightPanelTabs: { id: RightPanelTab; label: string; icon: React.ReactNode }[] = [
    { id: 'files', label: 'Files', icon: <FolderOpen className="w-4 h-4" /> },
    { id: 'terminal', label: 'Shell', icon: <TerminalIcon className="w-4 h-4" /> },
    { id: 'browser', label: 'Browser', icon: <Globe className="w-4 h-4" /> },
    { id: 'code', label: 'Editor', icon: <Code className="w-4 h-4" /> },
    { id: 'data', label: 'Data', icon: <Database className="w-4 h-4" /> },
  ];

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <PanelGroup direction="horizontal" className="flex-1">
        <Panel defaultSize={40} minSize={25}>
          <div className="h-full flex flex-col bg-kevin-bg">
            <ChatPanel
              messages={messages}
              loading={loading}
              error={error}
              onSendMessage={onSendMessage}
            />
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-kevin-primary hover:bg-kevin-accent transition-colors cursor-col-resize" />

        <Panel defaultSize={60} minSize={30}>
          <div className="h-full flex flex-col bg-kevin-bg">
            <div className="flex items-center justify-between border-b border-kevin-primary bg-kevin-surface">
              <div className="flex">
                {rightPanelTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveRightPanel(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors border-b-2 ${
                      activeRightPanel === tab.id
                        ? 'text-kevin-text border-kevin-accent bg-kevin-bg'
                        : 'text-kevin-muted hover:text-kevin-text border-transparent'
                    }`}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setShowPreview(!showPreview)}
                className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors ${
                  showPreview
                    ? 'text-kevin-accent'
                    : 'text-kevin-muted hover:text-kevin-text'
                }`}
              >
                <Eye className="w-4 h-4" />
                Preview
              </button>
            </div>

            <PanelGroup direction="vertical" className="flex-1">
              <Panel defaultSize={70} minSize={20}>
                <div className="h-full overflow-hidden">
                  {activeRightPanel === 'files' && (
                    <FileExplorer sessionId={sessionId} />
                  )}
                  {activeRightPanel === 'terminal' && (
                    <Terminal sessionId={sessionId} />
                  )}
                  {activeRightPanel === 'browser' && (
                    <BrowserPreview sessionId={sessionId} />
                  )}
                  {activeRightPanel === 'code' && (
                    <div className="h-full flex items-center justify-center text-kevin-muted">
                      <div className="text-center">
                        <Code className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>Code editor coming soon</p>
                      </div>
                    </div>
                  )}
                  {activeRightPanel === 'data' && (
                    <div className="h-full flex items-center justify-center text-kevin-muted">
                      <div className="text-center">
                        <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>Data analyst panel coming soon</p>
                      </div>
                    </div>
                  )}
                </div>
              </Panel>

              <PanelResizeHandle className="h-1 bg-kevin-primary hover:bg-kevin-accent transition-colors cursor-row-resize" />

              <Panel defaultSize={30} minSize={15}>
                <TodoPanel todos={todos} onUpdateTodos={onUpdateTodos} />
              </Panel>
            </PanelGroup>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}

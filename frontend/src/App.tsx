import { useState, useEffect } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { api } from './services/api';
import { useSession } from './hooks/useSession';
import { Sidebar } from './components/Sidebar';
import { ChatPanel } from './components/ChatPanel';
import { FileExplorer } from './components/FileExplorer';
import { Terminal } from './components/Terminal';
import { BrowserPreview } from './components/BrowserPreview';
import { TodoPanel } from './components/TodoPanel';
import { Header } from './components/Header';
import type { Session } from './types';

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [activeRightPanel, setActiveRightPanel] = useState<'files' | 'terminal' | 'browser'>('files');

  const {
    session,
    messages,
    todos,
    loading,
    error,
    isConnected,
    sendMessage,
    updateTodos,
  } = useSession(currentSessionId);

  // Load sessions on mount
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const data = await api.listSessions();
        setSessions(data);
        if (data.length > 0 && !currentSessionId) {
          setCurrentSessionId(data[0].id);
        }
      } catch (e) {
        console.error('Failed to load sessions:', e);
      }
    };
    loadSessions();
  }, [currentSessionId]);

  const handleCreateSession = async () => {
    try {
      const newSession = await api.createSession(`Session ${sessions.length + 1}`);
      setSessions((prev) => [...prev, newSession]);
      setCurrentSessionId(newSession.id);
    } catch (e) {
      console.error('Failed to create session:', e);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSessionId(sessions.length > 1 ? sessions[0].id : null);
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-kevin-bg text-kevin-text">
      <Header
        sessionName={session?.name || 'Kevin AI'}
        isConnected={isConnected}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={setCurrentSessionId}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
        />

        <PanelGroup direction="horizontal" className="flex-1">
          {/* Left Panel - Chat */}
          <Panel defaultSize={40} minSize={30}>
            <div className="h-full flex flex-col">
              <ChatPanel
                messages={messages}
                loading={loading}
                error={error}
                onSendMessage={sendMessage}
              />
            </div>
          </Panel>

          <PanelResizeHandle className="w-1 bg-kevin-primary hover:bg-kevin-accent transition-colors cursor-col-resize" />

          {/* Right Panel - Tools */}
          <Panel defaultSize={60} minSize={30}>
            <div className="h-full flex flex-col">
              {/* Panel Tabs */}
              <div className="flex border-b border-kevin-primary">
                <button
                  onClick={() => setActiveRightPanel('files')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeRightPanel === 'files'
                      ? 'bg-kevin-primary text-kevin-text border-b-2 border-kevin-accent'
                      : 'text-kevin-muted hover:text-kevin-text'
                  }`}
                >
                  Files
                </button>
                <button
                  onClick={() => setActiveRightPanel('terminal')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeRightPanel === 'terminal'
                      ? 'bg-kevin-primary text-kevin-text border-b-2 border-kevin-accent'
                      : 'text-kevin-muted hover:text-kevin-text'
                  }`}
                >
                  Terminal
                </button>
                <button
                  onClick={() => setActiveRightPanel('browser')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeRightPanel === 'browser'
                      ? 'bg-kevin-primary text-kevin-text border-b-2 border-kevin-accent'
                      : 'text-kevin-muted hover:text-kevin-text'
                  }`}
                >
                  Browser
                </button>
              </div>

              {/* Panel Content */}
              <PanelGroup direction="vertical" className="flex-1">
                <Panel defaultSize={70} minSize={20}>
                  <div className="h-full overflow-hidden">
                    {activeRightPanel === 'files' && (
                      <FileExplorer sessionId={currentSessionId} />
                    )}
                    {activeRightPanel === 'terminal' && (
                      <Terminal sessionId={currentSessionId} />
                    )}
                    {activeRightPanel === 'browser' && (
                      <BrowserPreview sessionId={currentSessionId} />
                    )}
                  </div>
                </Panel>

                <PanelResizeHandle className="h-1 bg-kevin-primary hover:bg-kevin-accent transition-colors cursor-row-resize" />

                {/* Todo Panel */}
                <Panel defaultSize={30} minSize={15}>
                  <TodoPanel
                    todos={todos}
                    onUpdateTodos={updateTodos}
                  />
                </Panel>
              </PanelGroup>
            </div>
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
}

export default App;

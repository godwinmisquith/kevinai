import { useState, useEffect } from 'react';
import { api } from './services/api';
import { useSession } from './hooks/useSession';
import { SessionSidebar } from './components/SessionSidebar';
import { LandingPage } from './components/LandingPage';
import { WorkspaceView } from './components/WorkspaceView';
import { AppHeader } from './components/AppHeader';
import type { Session } from './types';

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [agentMode, setAgentMode] = useState<'agent' | 'ask'>('agent');
  const [selectedMCPs, setSelectedMCPs] = useState<string[]>([]);
  const [showWorkspace, setShowWorkspace] = useState(false);

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

  useEffect(() => {
    const loadSessions = async () => {
      try {
        const data = await api.listSessions();
        setSessions(data);
      } catch (e) {
        console.error('Failed to load sessions:', e);
      }
    };
    loadSessions();
  }, []);

  useEffect(() => {
    if (currentSessionId && messages.length > 0) {
      setShowWorkspace(true);
    }
  }, [currentSessionId, messages.length]);

  const handleCreateSession = async () => {
    try {
      const newSession = await api.createSession(`Session ${sessions.length + 1}`);
      setSessions((prev) => [...prev, newSession]);
      setCurrentSessionId(newSession.id);
      return newSession;
    } catch (e) {
      console.error('Failed to create session:', e);
      return null;
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setShowWorkspace(false);
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setShowWorkspace(true);
  };

  const handleStartSession = async () => {
    if (!currentSessionId) {
      const newSession = await handleCreateSession();
      if (newSession) {
        setShowWorkspace(true);
      }
    } else {
      setShowWorkspace(true);
    }
  };

  const handleSendMessageFromLanding = async (message: string) => {
    if (!currentSessionId) {
      const newSession = await handleCreateSession();
      if (newSession) {
        setTimeout(() => {
          sendMessage(message);
        }, 100);
      }
    } else {
      sendMessage(message);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-kevin-bg text-kevin-text">
      <AppHeader
        userName={session?.name || 'Kevin AI'}
        agentMode={agentMode}
        onAgentModeChange={setAgentMode}
        isConnected={isConnected}
      />

      <div className="flex-1 flex overflow-hidden">
        <SessionSidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
        />

        {showWorkspace && currentSessionId ? (
          <WorkspaceView
            sessionId={currentSessionId}
            messages={messages}
            todos={todos}
            loading={loading}
            error={error}
            onSendMessage={sendMessage}
            onUpdateTodos={updateTodos}
          />
        ) : (
          <LandingPage
            onSendMessage={handleSendMessageFromLanding}
            onStartSession={handleStartSession}
            agentMode={agentMode}
            onAgentModeChange={setAgentMode}
            selectedMCPs={selectedMCPs}
            onMCPsChange={setSelectedMCPs}
          />
        )}
      </div>
    </div>
  );
}

export default App;

import { useState, useRef, useEffect } from 'react';
import { Terminal as TerminalIcon, Play, Square, Trash2 } from 'lucide-react';
import { api } from '../services/api';

interface TerminalProps {
  sessionId: string | null;
}

interface TerminalLine {
  id: string;
  type: 'input' | 'output' | 'error';
  content: string;
  timestamp: Date;
}

export function Terminal({ sessionId }: TerminalProps) {
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const [input, setInput] = useState('');
  const [currentDir, setCurrentDir] = useState('/home/ubuntu');
  const [isRunning, setIsRunning] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  // Focus input on click
  const handleTerminalClick = () => {
    inputRef.current?.focus();
  };

  const addLine = (type: TerminalLine['type'], content: string) => {
    setLines((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        type,
        content,
        timestamp: new Date(),
      },
    ]);
  };

  const executeCommand = async (command: string) => {
    if (!sessionId || !command.trim()) return;

    // Add command to history
    setHistory((prev) => [...prev, command]);
    setHistoryIndex(-1);

    // Add input line
    addLine('input', `${currentDir}$ ${command}`);

    // Handle built-in commands
    if (command === 'clear') {
      setLines([]);
      return;
    }

    if (command.startsWith('cd ')) {
      const newDir = command.slice(3).trim();
      if (newDir === '~') {
        setCurrentDir('/home/ubuntu');
      } else if (newDir.startsWith('/')) {
        setCurrentDir(newDir);
      } else if (newDir === '..') {
        const parts = currentDir.split('/');
        parts.pop();
        setCurrentDir(parts.join('/') || '/');
      } else {
        setCurrentDir(`${currentDir}/${newDir}`);
      }
      return;
    }

    setIsRunning(true);

    try {
      const result = await api.executeTool(sessionId, 'bash', {
        command,
        exec_dir: currentDir,
        timeout: 30000,
      });

      const output = result as {
        success?: boolean;
        result?: {
          stdout?: string;
          stderr?: string;
          return_code?: number;
        };
        error?: string;
      };

      if (output.success && output.result) {
        if (output.result.stdout) {
          addLine('output', output.result.stdout);
        }
        if (output.result.stderr) {
          addLine('error', output.result.stderr);
        }
        if (output.result.return_code !== 0) {
          addLine('error', `Exit code: ${output.result.return_code}`);
        }
      } else if (output.error) {
        addLine('error', output.error);
      }
    } catch (e) {
      addLine('error', e instanceof Error ? e.message : 'Command failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeCommand(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length > 0) {
        const newIndex = historyIndex < history.length - 1 ? historyIndex + 1 : historyIndex;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex] || '');
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex] || '');
      } else {
        setHistoryIndex(-1);
        setInput('');
      }
    } else if (e.key === 'c' && e.ctrlKey) {
      if (isRunning) {
        // Cancel running command (would need backend support)
        setIsRunning(false);
        addLine('error', '^C');
      }
    }
  };

  const handleClear = () => {
    setLines([]);
  };

  if (!sessionId) {
    return (
      <div className="h-full flex items-center justify-center text-kevin-muted">
        <p>Create or select a session to use the terminal</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-kevin-bg">
      {/* Toolbar */}
      <div className="flex items-center gap-2 p-2 border-b border-kevin-primary">
        <TerminalIcon className="w-4 h-4 text-kevin-accent" />
        <span className="text-sm font-medium">Terminal</span>
        <div className="flex-1" />
        <button
          onClick={handleClear}
          className="p-1 hover:bg-kevin-primary rounded transition-colors"
          title="Clear terminal"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Terminal Output */}
      <div
        ref={terminalRef}
        onClick={handleTerminalClick}
        className="flex-1 overflow-y-auto p-2 font-mono text-sm cursor-text"
      >
        {lines.length === 0 && (
          <div className="text-kevin-muted">
            <p>Kevin AI Terminal</p>
            <p>Type commands to execute them. Use 'clear' to clear the terminal.</p>
            <p className="mt-2">Current directory: {currentDir}</p>
          </div>
        )}
        {lines.map((line) => (
          <div
            key={line.id}
            className={`whitespace-pre-wrap break-all ${
              line.type === 'input'
                ? 'text-kevin-accent'
                : line.type === 'error'
                ? 'text-red-400'
                : 'text-kevin-text'
            }`}
          >
            {line.content}
          </div>
        ))}
        {isRunning && (
          <div className="flex items-center gap-2 text-kevin-muted">
            <div className="w-2 h-2 bg-kevin-accent rounded-full animate-pulse" />
            <span>Running...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-kevin-primary">
        <div className="flex items-center p-2 font-mono text-sm">
          <span className="text-kevin-accent mr-2">{currentDir}$</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isRunning}
            className="flex-1 bg-transparent outline-none text-kevin-text"
            placeholder={isRunning ? 'Running...' : 'Enter command...'}
            autoFocus
          />
          <button
            type="submit"
            disabled={isRunning || !input.trim()}
            className="p-1 hover:bg-kevin-primary rounded transition-colors disabled:opacity-50"
          >
            {isRunning ? (
              <Square className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

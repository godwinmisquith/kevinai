import { Bot, Wifi, WifiOff } from 'lucide-react';

interface HeaderProps {
  sessionName: string;
  isConnected: boolean;
}

export function Header({ sessionName, isConnected }: HeaderProps) {
  return (
    <header className="h-12 bg-kevin-surface border-b border-kevin-primary flex items-center justify-between px-4">
      <div className="flex items-center gap-3">
        <Bot className="w-6 h-6 text-kevin-accent" />
        <h1 className="text-lg font-semibold">Kevin AI</h1>
        <span className="text-kevin-muted text-sm">- {sessionName}</span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-green-500" />
              <span className="text-xs text-green-500">Connected</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-red-500" />
              <span className="text-xs text-red-500">Disconnected</span>
            </>
          )}
        </div>
        <span className="text-xs text-kevin-muted">Virtual AI Software Engineer</span>
      </div>
    </header>
  );
}

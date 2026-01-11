import { useState, useEffect } from 'react';
import {
  Folder,
  FolderOpen,
  File,
  FileCode,
  FileJson,
  FileText,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Home,
} from 'lucide-react';
import { api } from '../services/api';
import type { FileEntry } from '../types';

interface FileExplorerProps {
  sessionId: string | null;
}

interface FileTreeItemProps {
  entry: FileEntry;
  level: number;
  onSelect: (path: string) => void;
  selectedPath: string | null;
}

function FileTreeItem({ entry, level, onSelect, selectedPath }: FileTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [children, setChildren] = useState<FileEntry[]>([]);
  const [loading, setLoading] = useState(false);

  const isSelected = selectedPath === entry.path;

  const getFileIcon = (name: string, isDir: boolean) => {
    if (isDir) {
      return isExpanded ? (
        <FolderOpen className="w-4 h-4 text-yellow-500" />
      ) : (
        <Folder className="w-4 h-4 text-yellow-500" />
      );
    }

    const ext = name.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'ts':
      case 'tsx':
      case 'js':
      case 'jsx':
      case 'py':
      case 'go':
      case 'rs':
        return <FileCode className="w-4 h-4 text-blue-400" />;
      case 'json':
        return <FileJson className="w-4 h-4 text-yellow-400" />;
      case 'md':
      case 'txt':
        return <FileText className="w-4 h-4 text-gray-400" />;
      default:
        return <File className="w-4 h-4 text-gray-400" />;
    }
  };

  const handleClick = () => {
    if (entry.type === 'directory') {
      setIsExpanded(!isExpanded);
      if (!isExpanded && children.length === 0) {
        loadChildren();
      }
    }
    onSelect(entry.path);
  };

  const loadChildren = async () => {
    setLoading(true);
    // In a real implementation, this would call the API
    // For now, we'll just set empty children
    setChildren(entry.children || []);
    setLoading(false);
  };

  return (
    <div>
      <button
        onClick={handleClick}
        className={`w-full flex items-center gap-1 px-2 py-1 text-sm hover:bg-kevin-primary rounded transition-colors ${
          isSelected ? 'bg-kevin-primary' : ''
        }`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
      >
        {entry.type === 'directory' && (
          <span className="w-4 h-4 flex items-center justify-center">
            {loading ? (
              <RefreshCw className="w-3 h-3 animate-spin" />
            ) : isExpanded ? (
              <ChevronDown className="w-3 h-3" />
            ) : (
              <ChevronRight className="w-3 h-3" />
            )}
          </span>
        )}
        {entry.type === 'file' && <span className="w-4" />}
        {getFileIcon(entry.name, entry.type === 'directory')}
        <span className="truncate">{entry.name}</span>
        {entry.size !== undefined && (
          <span className="text-xs text-kevin-muted ml-auto">
            {formatFileSize(entry.size)}
          </span>
        )}
      </button>
      {isExpanded && children.length > 0 && (
        <div>
          {children.map((child) => (
            <FileTreeItem
              key={child.path}
              entry={child}
              level={level + 1}
              onSelect={onSelect}
              selectedPath={selectedPath}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileExplorer({ sessionId }: FileExplorerProps) {
  const [rootPath, setRootPath] = useState('/home/ubuntu');
  const [entries, setEntries] = useState<FileEntry[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDir = async () => {
      if (!sessionId) return;

      setLoading(true);
      setError(null);
      try {
        const result = await api.listDirectory(sessionId, rootPath);
        if (result.entries) {
          setEntries(result.entries);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load directory');
        setEntries([
          { name: 'src', type: 'directory', path: `${rootPath}/src` },
          { name: 'package.json', type: 'file', path: `${rootPath}/package.json`, size: 1024 },
          { name: 'README.md', type: 'file', path: `${rootPath}/README.md`, size: 2048 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadDir();
  }, [sessionId, rootPath]);

  const loadDirectory = async (path: string) => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);
    try {
      const result = await api.listDirectory(sessionId, path);
      if (result.entries) {
        setEntries(result.entries);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load directory');
      setEntries([
        { name: 'src', type: 'directory', path: `${path}/src` },
        { name: 'package.json', type: 'file', path: `${path}/package.json`, size: 1024 },
        { name: 'README.md', type: 'file', path: `${path}/README.md`, size: 2048 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectFile = async (path: string) => {
    setSelectedPath(path);
    if (!sessionId) return;

    // Check if it's a file (not a directory)
    const entry = entries.find((e) => e.path === path);
    if (entry?.type === 'file') {
      try {
        const result = await api.readFile(sessionId, path);
        setFileContent(result.content);
      } catch (e) {
        setFileContent(`Error loading file: ${e instanceof Error ? e.message : 'Unknown error'}`);
      }
    } else {
      setFileContent(null);
    }
  };

  const handleRefresh = () => {
    loadDirectory(rootPath);
  };

  const handleGoHome = () => {
    setRootPath('/home/ubuntu');
  };

  if (!sessionId) {
    return (
      <div className="h-full flex items-center justify-center text-kevin-muted">
        <p>Create or select a session to explore files</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-kevin-bg">
      {/* Toolbar */}
      <div className="flex items-center gap-2 p-2 border-b border-kevin-primary">
        <button
          onClick={handleGoHome}
          className="p-1 hover:bg-kevin-primary rounded transition-colors"
          title="Go to home"
        >
          <Home className="w-4 h-4" />
        </button>
        <button
          onClick={handleRefresh}
          className="p-1 hover:bg-kevin-primary rounded transition-colors"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
        <div className="flex-1 text-sm text-kevin-muted truncate px-2">
          {rootPath}
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto p-2">
        {error && (
          <div className="text-xs text-yellow-500 mb-2 px-2">
            Note: Using demo data. Connect to backend for real files.
          </div>
        )}
        {entries.map((entry) => (
          <FileTreeItem
            key={entry.path}
            entry={entry}
            level={0}
            onSelect={handleSelectFile}
            selectedPath={selectedPath}
          />
        ))}
      </div>

      {/* File Preview */}
      {fileContent && (
        <div className="h-1/3 border-t border-kevin-primary overflow-auto">
          <div className="p-2 bg-kevin-surface text-xs text-kevin-muted border-b border-kevin-primary">
            {selectedPath}
          </div>
          <pre className="p-2 text-xs overflow-auto">
            <code>{fileContent}</code>
          </pre>
        </div>
      )}
    </div>
  );
}

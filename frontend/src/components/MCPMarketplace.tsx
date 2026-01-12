import { useState, useEffect } from 'react';

interface MCPServer {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  author: string;
  version: string;
  tools: { name: string; description: string }[];
  resources: { uri: string; description: string }[];
  config_schema: Record<string, { type: string; required: boolean; secret?: boolean }>;
  requires_auth: boolean;
  auth_type: string | null;
  documentation_url: string | null;
  repository_url: string | null;
  downloads: number;
  rating: number;
  featured: boolean;
}

interface MCPCategory {
  id: string;
  name: string;
  count: number;
}

interface InstalledServer {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  connected: boolean;
  configured: boolean;
}

const API_BASE = 'http://localhost:8000/api';

const categoryIcons: Record<string, string> = {
  communication: '💬',
  project_management: '📋',
  development: '💻',
  documentation: '📄',
  database: '🗄️',
  cloud: '☁️',
  ai_ml: '🤖',
  analytics: '📊',
  security: '🔒',
  other: '🔧',
};

export function MCPMarketplace({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<'browse' | 'installed'>('browse');
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [installedServers, setInstalledServers] = useState<InstalledServer[]>([]);
  const [categories, setCategories] = useState<MCPCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);
  const [loading, setLoading] = useState(false);
  const [configuring, setConfiguring] = useState<string | null>(null);
  const [configValues, setConfigValues] = useState<Record<string, string>>({});

  useEffect(() => {
    loadCategories();
    loadServers();
    loadInstalledServers();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      searchServers(searchQuery);
    } else {
      loadServers(selectedCategory || undefined);
    }
  }, [selectedCategory, searchQuery]);

  const loadCategories = async () => {
    try {
      const res = await fetch(`${API_BASE}/mcp/marketplace/categories`);
      const data = await res.json();
      if (data.success) {
        setCategories(data.categories);
      }
    } catch (e) {
      console.error('Failed to load categories:', e);
    }
  };

  const loadServers = async (category?: string) => {
    setLoading(true);
    try {
      const url = category
        ? `${API_BASE}/mcp/marketplace?category=${category}`
        : `${API_BASE}/mcp/marketplace`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) {
        setServers(data.servers);
      }
    } catch (e) {
      console.error('Failed to load servers:', e);
    } finally {
      setLoading(false);
    }
  };

  const searchServers = async (query: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/mcp/marketplace/search?query=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (data.success) {
        setServers(data.servers);
      }
    } catch (e) {
      console.error('Failed to search servers:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadInstalledServers = async () => {
    try {
      const res = await fetch(`${API_BASE}/mcp/servers`);
      const data = await res.json();
      if (data.success) {
        setInstalledServers(data.servers);
      }
    } catch (e) {
      console.error('Failed to load installed servers:', e);
    }
  };

  const installServer = async (serverId: string) => {
    try {
      const res = await fetch(`${API_BASE}/mcp/servers/${serverId}/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      if (data.success) {
        loadInstalledServers();
        if (data.requires_config) {
          setConfiguring(serverId);
        }
      }
    } catch (e) {
      console.error('Failed to install server:', e);
    }
  };

  const uninstallServer = async (serverId: string) => {
    try {
      const res = await fetch(`${API_BASE}/mcp/servers/${serverId}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (data.success) {
        loadInstalledServers();
      }
    } catch (e) {
      console.error('Failed to uninstall server:', e);
    }
  };

  const configureServer = async (serverId: string) => {
    try {
      const res = await fetch(`${API_BASE}/mcp/servers/${serverId}/configure`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: configValues }),
      });
      const data = await res.json();
      if (data.success) {
        setConfiguring(null);
        setConfigValues({});
        loadInstalledServers();
      }
    } catch (e) {
      console.error('Failed to configure server:', e);
    }
  };

  const connectServer = async (serverId: string) => {
    try {
      const res = await fetch(`${API_BASE}/mcp/servers/${serverId}/connect`, {
        method: 'POST',
      });
      await res.json();
      loadInstalledServers();
    } catch (e) {
      console.error('Failed to connect server:', e);
    }
  };

  const disconnectServer = async (serverId: string) => {
    try {
      const res = await fetch(`${API_BASE}/mcp/servers/${serverId}/disconnect`, {
        method: 'POST',
      });
      await res.json();
      loadInstalledServers();
    } catch (e) {
      console.error('Failed to disconnect server:', e);
    }
  };

  const isInstalled = (serverId: string) => {
    return installedServers.some((s) => s.id === serverId);
  };

  const renderServerCard = (server: MCPServer) => {
    const installed = isInstalled(server.id);
    return (
      <div
        key={server.id}
        className="bg-kevin-surface border border-kevin-border rounded-lg p-4 hover:border-kevin-accent transition-colors cursor-pointer"
        onClick={() => setSelectedServer(server)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-kevin-bg rounded-lg flex items-center justify-center text-xl">
              {categoryIcons[server.category] || '🔧'}
            </div>
            <div>
              <h3 className="font-semibold text-kevin-text">{server.name}</h3>
              <p className="text-xs text-kevin-muted">{server.author}</p>
            </div>
          </div>
          {server.featured && (
            <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded">
              Featured
            </span>
          )}
        </div>
        <p className="text-sm text-kevin-muted mt-2 line-clamp-2">{server.description}</p>
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-3 text-xs text-kevin-muted">
            <span>{server.downloads.toLocaleString()} downloads</span>
            <span>v{server.version}</span>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (installed) {
                uninstallServer(server.id);
              } else {
                installServer(server.id);
              }
            }}
            className={`px-3 py-1 rounded text-sm ${
              installed
                ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                : 'bg-kevin-accent text-white hover:bg-kevin-accent/80'
            }`}
          >
            {installed ? 'Uninstall' : 'Install'}
          </button>
        </div>
      </div>
    );
  };

  const renderInstalledServerCard = (server: InstalledServer) => {
    return (
      <div
        key={server.id}
        className="bg-kevin-surface border border-kevin-border rounded-lg p-4"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-kevin-bg rounded-lg flex items-center justify-center text-xl">
              {categoryIcons[server.category] || '🔧'}
            </div>
            <div>
              <h3 className="font-semibold text-kevin-text">{server.name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`w-2 h-2 rounded-full ${
                    server.connected ? 'bg-green-500' : 'bg-gray-500'
                  }`}
                />
                <span className="text-xs text-kevin-muted">
                  {server.connected ? 'Connected' : 'Disconnected'}
                </span>
                {!server.configured && (
                  <span className="text-xs text-yellow-400">Needs configuration</span>
                )}
              </div>
            </div>
          </div>
        </div>
        <p className="text-sm text-kevin-muted mt-2">{server.description}</p>
        <div className="flex items-center gap-2 mt-3">
          {server.connected ? (
            <button
              onClick={() => disconnectServer(server.id)}
              className="px-3 py-1 bg-kevin-bg text-kevin-text rounded text-sm hover:bg-kevin-border"
            >
              Disconnect
            </button>
          ) : (
            <button
              onClick={() => connectServer(server.id)}
              className="px-3 py-1 bg-kevin-accent text-white rounded text-sm hover:bg-kevin-accent/80"
            >
              Connect
            </button>
          )}
          <button
            onClick={() => {
              setConfiguring(server.id);
              setConfigValues({});
            }}
            className="px-3 py-1 bg-kevin-bg text-kevin-text rounded text-sm hover:bg-kevin-border"
          >
            Configure
          </button>
          <button
            onClick={() => uninstallServer(server.id)}
            className="px-3 py-1 bg-red-500/20 text-red-400 rounded text-sm hover:bg-red-500/30"
          >
            Uninstall
          </button>
        </div>
      </div>
    );
  };

  const renderServerDetail = () => {
    if (!selectedServer) return null;

    const installed = isInstalled(selectedServer.id);

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-kevin-surface border border-kevin-border rounded-lg w-full max-w-2xl max-h-[80vh] overflow-hidden">
          <div className="p-6 border-b border-kevin-border">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-kevin-bg rounded-lg flex items-center justify-center text-2xl">
                  {categoryIcons[selectedServer.category] || '🔧'}
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-kevin-text">{selectedServer.name}</h2>
                  <p className="text-sm text-kevin-muted">by {selectedServer.author}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedServer(null)}
                className="text-kevin-muted hover:text-kevin-text"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="p-6 overflow-y-auto max-h-[60vh]">
            <p className="text-kevin-text mb-4">{selectedServer.description}</p>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-kevin-bg rounded-lg p-3">
                <p className="text-xs text-kevin-muted">Downloads</p>
                <p className="text-lg font-semibold text-kevin-text">
                  {selectedServer.downloads.toLocaleString()}
                </p>
              </div>
              <div className="bg-kevin-bg rounded-lg p-3">
                <p className="text-xs text-kevin-muted">Version</p>
                <p className="text-lg font-semibold text-kevin-text">{selectedServer.version}</p>
              </div>
              <div className="bg-kevin-bg rounded-lg p-3">
                <p className="text-xs text-kevin-muted">Rating</p>
                <p className="text-lg font-semibold text-kevin-text">
                  {'★'.repeat(Math.round(selectedServer.rating))} {selectedServer.rating}
                </p>
              </div>
            </div>

            {selectedServer.tools.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-kevin-text mb-2">
                  Tools ({selectedServer.tools.length})
                </h3>
                <div className="space-y-2">
                  {selectedServer.tools.map((tool) => (
                    <div key={tool.name} className="bg-kevin-bg rounded p-2">
                      <p className="text-sm font-medium text-kevin-text">{tool.name}</p>
                      <p className="text-xs text-kevin-muted">{tool.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedServer.resources.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-kevin-text mb-2">
                  Resources ({selectedServer.resources.length})
                </h3>
                <div className="space-y-2">
                  {selectedServer.resources.map((resource) => (
                    <div key={resource.uri} className="bg-kevin-bg rounded p-2">
                      <p className="text-sm font-mono text-kevin-accent">{resource.uri}</p>
                      <p className="text-xs text-kevin-muted">{resource.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedServer.requires_auth && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-kevin-text mb-2">Configuration Required</h3>
                <div className="bg-kevin-bg rounded p-3">
                  <p className="text-sm text-kevin-muted">
                    This server requires authentication ({selectedServer.auth_type}).
                  </p>
                  {Object.entries(selectedServer.config_schema).map(([key, schema]) => (
                    <div key={key} className="mt-2">
                      <span className="text-sm text-kevin-text">{key}</span>
                      {schema.required && <span className="text-red-400 ml-1">*</span>}
                      {schema.secret && (
                        <span className="text-xs text-kevin-muted ml-2">(secret)</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center gap-3">
              {selectedServer.documentation_url && (
                <a
                  href={selectedServer.documentation_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-kevin-accent hover:underline"
                >
                  Documentation
                </a>
              )}
              {selectedServer.repository_url && (
                <a
                  href={selectedServer.repository_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-kevin-accent hover:underline"
                >
                  Repository
                </a>
              )}
            </div>
          </div>

          <div className="p-4 border-t border-kevin-border flex justify-end gap-3">
            <button
              onClick={() => setSelectedServer(null)}
              className="px-4 py-2 bg-kevin-bg text-kevin-text rounded hover:bg-kevin-border"
            >
              Close
            </button>
            <button
              onClick={() => {
                if (installed) {
                  uninstallServer(selectedServer.id);
                } else {
                  installServer(selectedServer.id);
                }
                setSelectedServer(null);
              }}
              className={`px-4 py-2 rounded ${
                installed
                  ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                  : 'bg-kevin-accent text-white hover:bg-kevin-accent/80'
              }`}
            >
              {installed ? 'Uninstall' : 'Install'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderConfigModal = () => {
    if (!configuring) return null;

    const server = servers.find((s) => s.id === configuring);
    if (!server) return null;

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-kevin-surface border border-kevin-border rounded-lg w-full max-w-md p-6">
          <h2 className="text-lg font-semibold text-kevin-text mb-4">
            Configure {server.name}
          </h2>

          <div className="space-y-4">
            {Object.entries(server.config_schema).map(([key, schema]) => (
              <div key={key}>
                <label className="block text-sm text-kevin-text mb-1">
                  {key}
                  {schema.required && <span className="text-red-400 ml-1">*</span>}
                </label>
                <input
                  type={schema.secret ? 'password' : 'text'}
                  value={configValues[key] || ''}
                  onChange={(e) =>
                    setConfigValues((prev) => ({ ...prev, [key]: e.target.value }))
                  }
                  className="w-full px-3 py-2 bg-kevin-bg border border-kevin-border rounded text-kevin-text focus:outline-none focus:border-kevin-accent"
                  placeholder={`Enter ${key}`}
                />
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              onClick={() => {
                setConfiguring(null);
                setConfigValues({});
              }}
              className="px-4 py-2 bg-kevin-bg text-kevin-text rounded hover:bg-kevin-border"
            >
              Cancel
            </button>
            <button
              onClick={() => configureServer(configuring)}
              className="px-4 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
      <div className="bg-kevin-bg border border-kevin-border rounded-lg w-full max-w-5xl h-[80vh] flex flex-col">
        <div className="p-4 border-b border-kevin-border flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold text-kevin-text">MCP Marketplace</h1>
            <div className="flex bg-kevin-surface rounded-lg p-1">
              <button
                onClick={() => setActiveTab('browse')}
                className={`px-4 py-1.5 rounded text-sm ${
                  activeTab === 'browse'
                    ? 'bg-kevin-accent text-white'
                    : 'text-kevin-muted hover:text-kevin-text'
                }`}
              >
                Browse
              </button>
              <button
                onClick={() => setActiveTab('installed')}
                className={`px-4 py-1.5 rounded text-sm ${
                  activeTab === 'installed'
                    ? 'bg-kevin-accent text-white'
                    : 'text-kevin-muted hover:text-kevin-text'
                }`}
              >
                Installed ({installedServers.length})
              </button>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-kevin-muted hover:text-kevin-text text-xl"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {activeTab === 'browse' && (
            <>
              <div className="w-48 border-r border-kevin-border p-4 overflow-y-auto">
                <h2 className="text-sm font-semibold text-kevin-muted mb-3">Categories</h2>
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`w-full text-left px-3 py-2 rounded text-sm ${
                    selectedCategory === null
                      ? 'bg-kevin-accent text-white'
                      : 'text-kevin-text hover:bg-kevin-surface'
                  }`}
                >
                  All Servers
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`w-full text-left px-3 py-2 rounded text-sm flex items-center justify-between ${
                      selectedCategory === cat.id
                        ? 'bg-kevin-accent text-white'
                        : 'text-kevin-text hover:bg-kevin-surface'
                    }`}
                  >
                    <span>
                      {categoryIcons[cat.id]} {cat.name}
                    </span>
                    <span className="text-xs opacity-60">{cat.count}</span>
                  </button>
                ))}
              </div>

              <div className="flex-1 p-4 overflow-y-auto">
                <div className="mb-4">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search MCP servers..."
                    className="w-full px-4 py-2 bg-kevin-surface border border-kevin-border rounded-lg text-kevin-text focus:outline-none focus:border-kevin-accent"
                  />
                </div>

                {loading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="text-kevin-muted">Loading...</div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    {servers.map(renderServerCard)}
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'installed' && (
            <div className="flex-1 p-4 overflow-y-auto">
              {installedServers.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-kevin-muted">
                  <p className="text-lg mb-2">No MCP servers installed</p>
                  <p className="text-sm">Browse the marketplace to install servers</p>
                  <button
                    onClick={() => setActiveTab('browse')}
                    className="mt-4 px-4 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80"
                  >
                    Browse Marketplace
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {installedServers.map(renderInstalledServerCard)}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {renderServerDetail()}
      {renderConfigModal()}
    </div>
  );
}

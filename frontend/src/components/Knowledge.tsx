import { useState, useEffect } from 'react';

interface KnowledgeEntry {
  id: string;
  title: string;
  trigger_description: string;
  content: string;
  scope: string;
  pinned_repos: string[];
  source: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  tags: string[];
  is_active: boolean;
  access_count: number;
  last_accessed: string | null;
}

interface KnowledgeSuggestion {
  id: string;
  title: string;
  trigger_description: string;
  content: string;
  suggested_scope: string;
  suggested_repos: string[];
  source_session_id: string;
  source_message: string;
  created_at: string;
  status: string;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const scopeLabels: Record<string, string> = {
  no_repos: 'No repos (trigger-based)',
  specific_repos: 'Specific repos',
  all_repos: 'All repos',
};

const sourceLabels: Record<string, string> = {
  user: 'User created',
  auto_generated: 'Auto-generated',
  suggested: 'From suggestion',
  imported: 'Imported',
};

const tagColors = [
  'bg-blue-500/20 text-blue-400',
  'bg-green-500/20 text-green-400',
  'bg-purple-500/20 text-purple-400',
  'bg-yellow-500/20 text-yellow-400',
  'bg-pink-500/20 text-pink-400',
  'bg-cyan-500/20 text-cyan-400',
];

export function Knowledge({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<'knowledge' | 'suggestions'>('knowledge');
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [suggestions, setSuggestions] = useState<KnowledgeSuggestion[]>([]);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [editingEntry, setEditingEntry] = useState<KnowledgeEntry | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    trigger_description: '',
    content: '',
    scope: 'no_repos',
    pinned_repos: [] as string[],
    tags: [] as string[],
  });
  const [newTag, setNewTag] = useState('');
  const [newRepo, setNewRepo] = useState('');

  useEffect(() => {
    loadEntries();
    loadTags();
    loadSuggestions();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      searchEntries(searchQuery);
    } else if (selectedTag) {
      loadEntriesByTag(selectedTag);
    } else {
      loadEntries();
    }
  }, [selectedTag, searchQuery]);

  const loadEntries = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/knowledge`);
      const data = await res.json();
      setEntries(data.entries || []);
    } catch (e) {
      console.error('Failed to load knowledge:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadTags = async () => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/tags`);
      const data = await res.json();
      setAllTags(data.tags || []);
    } catch (e) {
      console.error('Failed to load tags:', e);
    }
  };

  const loadSuggestions = async () => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/suggestions?status=pending`);
      const data = await res.json();
      setSuggestions(data.suggestions || []);
    } catch (e) {
      console.error('Failed to load suggestions:', e);
    }
  };

  const searchEntries = async (query: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/knowledge/search?query=${encodeURIComponent(query)}`);
      const data = await res.json();
      setEntries(data.entries || []);
    } catch (e) {
      console.error('Failed to search knowledge:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadEntriesByTag = async (tag: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/knowledge/tag/${encodeURIComponent(tag)}`);
      const data = await res.json();
      setEntries(data.entries || []);
    } catch (e) {
      console.error('Failed to load knowledge by tag:', e);
    } finally {
      setLoading(false);
    }
  };

  const createEntry = async () => {
    try {
      const res = await fetch(`${API_BASE}/knowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.entry) {
        setCreatingNew(false);
        resetForm();
        loadEntries();
        loadTags();
      }
    } catch (e) {
      console.error('Failed to create knowledge:', e);
    }
  };

  const updateEntry = async () => {
    if (!editingEntry) return;
    try {
      const res = await fetch(`${API_BASE}/knowledge/${editingEntry.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.entry) {
        setEditingEntry(null);
        resetForm();
        loadEntries();
        loadTags();
      }
    } catch (e) {
      console.error('Failed to update knowledge:', e);
    }
  };

  const deleteEntry = async (entryId: string) => {
    try {
      await fetch(`${API_BASE}/knowledge/${entryId}`, {
        method: 'DELETE',
      });
      loadEntries();
      setSelectedEntry(null);
    } catch (e) {
      console.error('Failed to delete knowledge:', e);
    }
  };

  const acceptSuggestion = async (suggestionId: string) => {
    try {
      await fetch(`${API_BASE}/knowledge/suggestions/${suggestionId}/accept`, {
        method: 'POST',
      });
      loadSuggestions();
      loadEntries();
    } catch (e) {
      console.error('Failed to accept suggestion:', e);
    }
  };

  const dismissSuggestion = async (suggestionId: string) => {
    try {
      await fetch(`${API_BASE}/knowledge/suggestions/${suggestionId}/dismiss`, {
        method: 'POST',
      });
      loadSuggestions();
    } catch (e) {
      console.error('Failed to dismiss suggestion:', e);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      trigger_description: '',
      content: '',
      scope: 'no_repos',
      pinned_repos: [],
      tags: [],
    });
    setNewTag('');
    setNewRepo('');
  };

  const startEditing = (entry: KnowledgeEntry) => {
    setEditingEntry(entry);
    setFormData({
      title: entry.title,
      trigger_description: entry.trigger_description,
      content: entry.content,
      scope: entry.scope,
      pinned_repos: entry.pinned_repos,
      tags: entry.tags,
    });
  };

  const addTag = () => {
    if (newTag && !formData.tags.includes(newTag)) {
      setFormData((prev) => ({ ...prev, tags: [...prev.tags, newTag] }));
      setNewTag('');
    }
  };

  const removeTag = (tag: string) => {
    setFormData((prev) => ({ ...prev, tags: prev.tags.filter((t) => t !== tag) }));
  };

  const addRepo = () => {
    if (newRepo && !formData.pinned_repos.includes(newRepo)) {
      setFormData((prev) => ({ ...prev, pinned_repos: [...prev.pinned_repos, newRepo] }));
      setNewRepo('');
    }
  };

  const removeRepo = (repo: string) => {
    setFormData((prev) => ({
      ...prev,
      pinned_repos: prev.pinned_repos.filter((r) => r !== repo),
    }));
  };

  const getTagColor = (tag: string) => {
    const index = tag.charCodeAt(0) % tagColors.length;
    return tagColors[index];
  };

  const renderEntryCard = (entry: KnowledgeEntry) => {
    return (
      <div
        key={entry.id}
        className="bg-kevin-surface border border-kevin-border rounded-lg p-4 hover:border-kevin-accent transition-colors cursor-pointer"
        onClick={() => setSelectedEntry(entry)}
      >
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-kevin-text">{entry.title}</h3>
            <p className="text-xs text-kevin-muted mt-1">{entry.trigger_description}</p>
          </div>
          <div className="flex items-center gap-2">
            {!entry.is_active && (
              <span className="px-2 py-0.5 bg-gray-500/20 text-gray-400 text-xs rounded">
                Inactive
              </span>
            )}
            <span className="px-2 py-0.5 bg-kevin-bg text-kevin-muted text-xs rounded">
              {scopeLabels[entry.scope]}
            </span>
          </div>
        </div>
        <p className="text-sm text-kevin-muted mt-2 line-clamp-2">{entry.content}</p>
        <div className="flex items-center justify-between mt-3">
          <div className="flex flex-wrap gap-1">
            {entry.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className={`px-2 py-0.5 text-xs rounded ${getTagColor(tag)}`}
              >
                {tag}
              </span>
            ))}
            {entry.tags.length > 3 && (
              <span className="px-2 py-0.5 text-xs text-kevin-muted">
                +{entry.tags.length - 3} more
              </span>
            )}
          </div>
          <span className="text-xs text-kevin-muted">
            {entry.access_count} accesses
          </span>
        </div>
      </div>
    );
  };

  const renderSuggestionCard = (suggestion: KnowledgeSuggestion) => {
    return (
      <div
        key={suggestion.id}
        className="bg-kevin-surface border border-yellow-500/30 rounded-lg p-4"
      >
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-kevin-text">{suggestion.title}</h3>
            <p className="text-xs text-kevin-muted mt-1">{suggestion.trigger_description}</p>
          </div>
          <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded">
            Suggested
          </span>
        </div>
        <p className="text-sm text-kevin-muted mt-2 line-clamp-2">{suggestion.content}</p>
        {suggestion.source_message && (
          <p className="text-xs text-kevin-muted mt-2 italic">
            From: "{suggestion.source_message.slice(0, 100)}..."
          </p>
        )}
        <div className="flex items-center gap-2 mt-3">
          <button
            onClick={() => acceptSuggestion(suggestion.id)}
            className="px-3 py-1 bg-kevin-accent text-white rounded text-sm hover:bg-kevin-accent/80"
          >
            Accept
          </button>
          <button
            onClick={() => dismissSuggestion(suggestion.id)}
            className="px-3 py-1 bg-kevin-bg text-kevin-text rounded text-sm hover:bg-kevin-border"
          >
            Dismiss
          </button>
        </div>
      </div>
    );
  };

  const renderEntryDetail = () => {
    if (!selectedEntry) return null;

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-kevin-surface border border-kevin-border rounded-lg w-full max-w-2xl max-h-[80vh] overflow-hidden">
          <div className="p-6 border-b border-kevin-border">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-semibold text-kevin-text">{selectedEntry.title}</h2>
                <p className="text-sm text-kevin-muted mt-1">{sourceLabels[selectedEntry.source]}</p>
              </div>
              <button
                onClick={() => setSelectedEntry(null)}
                className="text-kevin-muted hover:text-kevin-text"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="p-6 overflow-y-auto max-h-[60vh]">
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-kevin-text mb-1">Trigger Description</h3>
              <p className="text-sm text-kevin-muted bg-kevin-bg rounded p-3">
                {selectedEntry.trigger_description}
              </p>
            </div>

            <div className="mb-4">
              <h3 className="text-sm font-semibold text-kevin-text mb-1">Content</h3>
              <p className="text-sm text-kevin-text bg-kevin-bg rounded p-3 whitespace-pre-wrap">
                {selectedEntry.content}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <h3 className="text-sm font-semibold text-kevin-text mb-1">Scope</h3>
                <p className="text-sm text-kevin-muted">{scopeLabels[selectedEntry.scope]}</p>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-kevin-text mb-1">Status</h3>
                <p className="text-sm text-kevin-muted">
                  {selectedEntry.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>

            {selectedEntry.pinned_repos.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-kevin-text mb-1">Pinned Repos</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedEntry.pinned_repos.map((repo) => (
                    <span
                      key={repo}
                      className="px-2 py-1 bg-kevin-bg text-kevin-text text-sm rounded"
                    >
                      {repo}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedEntry.tags.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-kevin-text mb-1">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedEntry.tags.map((tag) => (
                    <span key={tag} className={`px-2 py-1 text-sm rounded ${getTagColor(tag)}`}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-xs text-kevin-muted">
              <div>
                <span>Created: {new Date(selectedEntry.created_at).toLocaleDateString()}</span>
              </div>
              <div>
                <span>Updated: {new Date(selectedEntry.updated_at).toLocaleDateString()}</span>
              </div>
              <div>
                <span>Accesses: {selectedEntry.access_count}</span>
              </div>
              {selectedEntry.last_accessed && (
                <div>
                  <span>
                    Last accessed: {new Date(selectedEntry.last_accessed).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="p-4 border-t border-kevin-border flex justify-end gap-3">
            <button
              onClick={() => {
                setSelectedEntry(null);
                startEditing(selectedEntry);
              }}
              className="px-4 py-2 bg-kevin-bg text-kevin-text rounded hover:bg-kevin-border"
            >
              Edit
            </button>
            <button
              onClick={() => deleteEntry(selectedEntry.id)}
              className="px-4 py-2 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30"
            >
              Delete
            </button>
            <button
              onClick={() => setSelectedEntry(null)}
              className="px-4 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderForm = () => {
    if (!creatingNew && !editingEntry) return null;

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-kevin-surface border border-kevin-border rounded-lg w-full max-w-2xl max-h-[80vh] overflow-hidden">
          <div className="p-6 border-b border-kevin-border">
            <div className="flex items-start justify-between">
              <h2 className="text-xl font-semibold text-kevin-text">
                {editingEntry ? 'Edit Knowledge' : 'Add Knowledge'}
              </h2>
              <button
                onClick={() => {
                  setCreatingNew(false);
                  setEditingEntry(null);
                  resetForm();
                }}
                className="text-kevin-muted hover:text-kevin-text"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="p-6 overflow-y-auto max-h-[60vh] space-y-4">
            <div>
              <label className="block text-sm font-medium text-kevin-text mb-1">Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full bg-kevin-bg border border-kevin-border rounded px-3 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent"
                placeholder="e.g., Python Code Style"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-kevin-text mb-1">
                Trigger Description *
              </label>
              <input
                type="text"
                value={formData.trigger_description}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, trigger_description: e.target.value }))
                }
                className="w-full bg-kevin-bg border border-kevin-border rounded px-3 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent"
                placeholder="When should Kevin recall this knowledge?"
              />
              <p className="text-xs text-kevin-muted mt-1">
                This helps Kevin know when to use this knowledge
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-kevin-text mb-1">Content *</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData((prev) => ({ ...prev, content: e.target.value }))}
                rows={5}
                className="w-full bg-kevin-bg border border-kevin-border rounded px-3 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent resize-none"
                placeholder="The knowledge content..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-kevin-text mb-1">Scope</label>
              <select
                value={formData.scope}
                onChange={(e) => setFormData((prev) => ({ ...prev, scope: e.target.value }))}
                className="w-full bg-kevin-bg border border-kevin-border rounded px-3 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent"
              >
                <option value="no_repos">No repos (trigger-based only)</option>
                <option value="specific_repos">Specific repos</option>
                <option value="all_repos">All repos</option>
              </select>
            </div>

            {formData.scope === 'specific_repos' && (
              <div>
                <label className="block text-sm font-medium text-kevin-text mb-1">
                  Pinned Repos
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={newRepo}
                    onChange={(e) => setNewRepo(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addRepo())}
                    className="flex-1 bg-kevin-bg border border-kevin-border rounded px-3 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent"
                    placeholder="Repository name"
                  />
                  <button
                    onClick={addRepo}
                    className="px-3 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.pinned_repos.map((repo) => (
                    <span
                      key={repo}
                      className="px-2 py-1 bg-kevin-bg text-kevin-text text-sm rounded flex items-center gap-1"
                    >
                      {repo}
                      <button
                        onClick={() => removeRepo(repo)}
                        className="text-kevin-muted hover:text-red-400"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-kevin-text mb-1">Tags</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  className="flex-1 bg-kevin-bg border border-kevin-border rounded px-3 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent"
                  placeholder="Add a tag"
                />
                <button
                  onClick={addTag}
                  className="px-3 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag) => (
                  <span
                    key={tag}
                    className={`px-2 py-1 text-sm rounded flex items-center gap-1 ${getTagColor(tag)}`}
                  >
                    {tag}
                    <button
                      onClick={() => removeTag(tag)}
                      className="hover:text-red-400"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="p-4 border-t border-kevin-border flex justify-end gap-3">
            <button
              onClick={() => {
                setCreatingNew(false);
                setEditingEntry(null);
                resetForm();
              }}
              className="px-4 py-2 bg-kevin-bg text-kevin-text rounded hover:bg-kevin-border"
            >
              Cancel
            </button>
            <button
              onClick={editingEntry ? updateEntry : createEntry}
              disabled={!formData.title || !formData.trigger_description || !formData.content}
              className="px-4 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {editingEntry ? 'Save Changes' : 'Create Knowledge'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
      <div className="bg-kevin-bg border border-kevin-border rounded-lg w-full max-w-4xl h-[80vh] flex flex-col">
        <div className="p-4 border-b border-kevin-border flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold text-kevin-text">Knowledge</h1>
            <div className="flex bg-kevin-surface rounded-lg p-1">
              <button
                onClick={() => setActiveTab('knowledge')}
                className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
                  activeTab === 'knowledge'
                    ? 'bg-kevin-primary text-kevin-text'
                    : 'text-kevin-muted hover:text-kevin-text'
                }`}
              >
                Knowledge ({entries.length})
              </button>
              <button
                onClick={() => setActiveTab('suggestions')}
                className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
                  activeTab === 'suggestions'
                    ? 'bg-kevin-primary text-kevin-text'
                    : 'text-kevin-muted hover:text-kevin-text'
                }`}
              >
                Suggestions ({suggestions.length})
              </button>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCreatingNew(true)}
              className="px-4 py-2 bg-kevin-accent text-white rounded hover:bg-kevin-accent/80"
            >
              Add Knowledge
            </button>
            <button
              onClick={onClose}
              className="text-kevin-muted hover:text-kevin-text text-xl"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="flex-1 flex overflow-hidden">
          {activeTab === 'knowledge' && (
            <>
              <div className="w-48 border-r border-kevin-border p-4 overflow-y-auto">
                <h3 className="text-sm font-semibold text-kevin-text mb-3">Filter by Tag</h3>
                <button
                  onClick={() => {
                    setSelectedTag(null);
                    setSearchQuery('');
                  }}
                  className={`w-full text-left px-3 py-2 rounded text-sm mb-1 ${
                    !selectedTag
                      ? 'bg-kevin-primary text-kevin-text'
                      : 'text-kevin-muted hover:bg-kevin-surface'
                  }`}
                >
                  All
                </button>
                {allTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => {
                      setSelectedTag(tag);
                      setSearchQuery('');
                    }}
                    className={`w-full text-left px-3 py-2 rounded text-sm mb-1 ${
                      selectedTag === tag
                        ? 'bg-kevin-primary text-kevin-text'
                        : 'text-kevin-muted hover:bg-kevin-surface'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>

              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="p-4 border-b border-kevin-border">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setSelectedTag(null);
                    }}
                    placeholder="Search knowledge..."
                    className="w-full bg-kevin-surface border border-kevin-border rounded px-4 py-2 text-kevin-text focus:outline-none focus:border-kevin-accent"
                  />
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                  {loading ? (
                    <div className="flex items-center justify-center h-full">
                      <span className="text-kevin-muted">Loading...</span>
                    </div>
                  ) : entries.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-kevin-muted">
                      <p>No knowledge entries found</p>
                      <button
                        onClick={() => setCreatingNew(true)}
                        className="mt-2 text-kevin-accent hover:underline"
                      >
                        Add your first knowledge entry
                      </button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-4">
                      {entries.map(renderEntryCard)}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {activeTab === 'suggestions' && (
            <div className="flex-1 overflow-y-auto p-4">
              {suggestions.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-kevin-muted">
                  <p>No pending suggestions</p>
                  <p className="text-sm mt-1">
                    Kevin will suggest knowledge based on your conversations
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {suggestions.map(renderSuggestionCard)}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {renderEntryDetail()}
      {renderForm()}
    </div>
  );
}

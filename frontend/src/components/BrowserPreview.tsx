import { useState } from 'react';
import {
  Globe,
  RefreshCw,
  ArrowLeft,
  ArrowRight,
  ExternalLink,
  Camera,
} from 'lucide-react';
import { api } from '../services/api';

interface BrowserPreviewProps {
  sessionId: string | null;
}

export function BrowserPreview({ sessionId }: BrowserPreviewProps) {
  const [url, setUrl] = useState('');
  const [currentUrl, setCurrentUrl] = useState('');
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pageTitle, setPageTitle] = useState('');

  const navigateTo = async (targetUrl: string) => {
    if (!sessionId || !targetUrl.trim()) return;

    // Add protocol if missing
    let fullUrl = targetUrl;
    if (!fullUrl.startsWith('http://') && !fullUrl.startsWith('https://')) {
      fullUrl = `https://${fullUrl}`;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.executeTool(sessionId, 'browser_navigate', {
        url: fullUrl,
      });

      const response = result as {
        success?: boolean;
        result?: {
          url?: string;
          title?: string;
        };
        error?: string;
      };

      if (response.success && response.result) {
        setCurrentUrl(response.result.url || fullUrl);
        setPageTitle(response.result.title || '');
        // Take a screenshot after navigation
        await takeScreenshot();
      } else if (response.error) {
        setError(response.error);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Navigation failed');
    } finally {
      setLoading(false);
    }
  };

  const takeScreenshot = async () => {
    if (!sessionId) return;

    try {
      const result = await api.executeTool(sessionId, 'browser_screenshot', {
        full_page: false,
      });

      const response = result as {
        success?: boolean;
        result?: {
          screenshot?: string;
        };
        error?: string;
      };

      if (response.success && response.result?.screenshot) {
        setScreenshot(`data:image/png;base64,${response.result.screenshot}`);
      }
    } catch (e) {
      console.error('Screenshot failed:', e);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigateTo(url);
  };

  const handleRefresh = () => {
    if (currentUrl) {
      navigateTo(currentUrl);
    }
  };

  const handleOpenExternal = () => {
    if (currentUrl) {
      window.open(currentUrl, '_blank');
    }
  };

  if (!sessionId) {
    return (
      <div className="h-full flex items-center justify-center text-kevin-muted">
        <p>Create or select a session to use the browser</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-kevin-bg">
      {/* Browser Toolbar */}
      <div className="flex items-center gap-2 p-2 border-b border-kevin-primary">
        <button
          className="p-1 hover:bg-kevin-primary rounded transition-colors disabled:opacity-50"
          disabled
          title="Back"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <button
          className="p-1 hover:bg-kevin-primary rounded transition-colors disabled:opacity-50"
          disabled
          title="Forward"
        >
          <ArrowRight className="w-4 h-4" />
        </button>
        <button
          onClick={handleRefresh}
          className="p-1 hover:bg-kevin-primary rounded transition-colors"
          title="Refresh"
          disabled={!currentUrl || loading}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>

        <form onSubmit={handleSubmit} className="flex-1 flex">
          <div className="flex-1 flex items-center bg-kevin-surface rounded-lg px-3 py-1">
            <Globe className="w-4 h-4 text-kevin-muted mr-2" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL..."
              className="flex-1 bg-transparent outline-none text-sm"
            />
          </div>
        </form>

        <button
          onClick={takeScreenshot}
          className="p-1 hover:bg-kevin-primary rounded transition-colors"
          title="Take screenshot"
          disabled={!currentUrl}
        >
          <Camera className="w-4 h-4" />
        </button>
        <button
          onClick={handleOpenExternal}
          className="p-1 hover:bg-kevin-primary rounded transition-colors"
          title="Open in new tab"
          disabled={!currentUrl}
        >
          <ExternalLink className="w-4 h-4" />
        </button>
      </div>

      {/* Page Title */}
      {pageTitle && (
        <div className="px-3 py-1 text-xs text-kevin-muted border-b border-kevin-primary truncate">
          {pageTitle}
        </div>
      )}

      {/* Browser Content */}
      <div className="flex-1 overflow-auto bg-white">
        {!currentUrl && !screenshot && (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 bg-kevin-surface">
            <Globe className="w-16 h-16 mb-4 text-kevin-accent" />
            <h3 className="text-lg font-medium mb-2">Browser Preview</h3>
            <p className="text-sm text-kevin-muted text-center max-w-md">
              Enter a URL above to navigate. Kevin can automate browser
              interactions like clicking, typing, and scrolling.
            </p>
          </div>
        )}

        {loading && (
          <div className="h-full flex items-center justify-center bg-kevin-surface">
            <div className="flex flex-col items-center">
              <RefreshCw className="w-8 h-8 animate-spin text-kevin-accent mb-2" />
              <span className="text-sm text-kevin-muted">Loading...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="h-full flex items-center justify-center bg-kevin-surface">
            <div className="text-center p-4">
              <p className="text-red-400 mb-2">Failed to load page</p>
              <p className="text-sm text-kevin-muted">{error}</p>
            </div>
          </div>
        )}

        {screenshot && !loading && (
          <div className="h-full overflow-auto">
            <img
              src={screenshot}
              alt="Browser screenshot"
              className="w-full h-auto"
            />
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="px-3 py-1 text-xs text-kevin-muted border-t border-kevin-primary flex items-center justify-between">
        <span>{currentUrl || 'No page loaded'}</span>
        {loading && <span>Loading...</span>}
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Search, Loader2, AlertCircle } from 'lucide-react';
import { YouTubeIcon } from './Icons';
import type { PlatformType } from '../types';

interface UrlInputProps {
  selectedPlatform: PlatformType;
  onPlatformChange: (p: PlatformType) => void;
  onAnalyze: (url: string, sampleLimit: number) => void;
  isLoading: boolean;
  error: string | null;
  isXAvailable?: boolean;
}

const SAMPLE_LIMITS = [50, 100, 200, 500];

export const UrlInput: React.FC<UrlInputProps> = ({
  selectedPlatform,
  onPlatformChange,
  onAnalyze,
  isLoading,
  error,
  isXAvailable = false,
}) => {
  const [url, setUrl] = useState('');
  const [sampleLimit, setSampleLimit] = useState(100);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || isLoading) return;
    onAnalyze(url.trim(), sampleLimit);
  };

  return (
    <div className="glass-card analyzer-card">
      {/* Platform Selection */}
      <div className="platform-selector">
        <button
          type="button"
          id="btn-platform-youtube"
          className={`platform-tab ${selectedPlatform === 'youtube' ? 'active' : ''}`}
          onClick={() => onPlatformChange('youtube')}
        >
          <YouTubeIcon size={18} color={selectedPlatform === 'youtube' ? '#ff0033' : 'currentColor'} />
          <span>YouTube</span>
        </button>

        <button
          type="button"
          id="btn-platform-x"
          className={`platform-tab x-tab ${selectedPlatform === 'x' ? 'active' : ''}`}
          onClick={() => isXAvailable && onPlatformChange('x')}
          disabled={!isXAvailable}
          title={isXAvailable ? 'Analyze X.com / Twitter post' : 'Available in Phase 2'}
        >
          <span style={{ fontWeight: 800, fontSize: '0.9rem' }}>𝕏</span>
          <span>X.com</span>
          {!isXAvailable && <span className="badge-phase">Phase 2</span>}
        </button>
      </div>

      {/* URL Input Form */}
      <form onSubmit={handleSubmit}>
        <div className="input-row">
          <div className="input-wrapper">
            <Search className="input-icon" size={18} />
            <input
              id="input-target-url"
              type="text"
              className="url-input"
              placeholder={
                selectedPlatform === 'youtube'
                  ? 'Paste YouTube URL (e.g., https://www.youtube.com/watch?v=... or shorts)'
                  : 'Paste X.com post URL (e.g., https://x.com/user/status/...)'
              }
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isLoading}
              required
            />
          </div>

          <button
            id="btn-analyze-submit"
            type="submit"
            className="analyze-button"
            disabled={isLoading || !url.trim()}
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                <span>Extracting & Analyzing...</span>
              </>
            ) : (
              <span>Analyze Sentiment</span>
            )}
          </button>
        </div>

        {/* Sample Limit Selector */}
        <div className="sample-limit-row">
          <span>Max Comments Sample Limit:</span>
          <div className="limit-pills">
            {SAMPLE_LIMITS.map((limit) => (
              <button
                key={limit}
                type="button"
                className={`limit-pill ${sampleLimit === limit ? 'active' : ''}`}
                onClick={() => setSampleLimit(limit)}
                disabled={isLoading}
              >
                {limit}
              </button>
            ))}
          </div>
        </div>
      </form>

      {/* Actionable Error State */}
      {error && (
        <div className="alert-banner error" role="alert">
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Analysis Failed: </strong>
            <span>{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

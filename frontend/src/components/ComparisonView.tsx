import React, { useState } from 'react';
import { ArrowLeftRight, Loader2, AlertCircle, Trophy, Flame, ThumbsDown, Eye, Heart } from 'lucide-react';
import type { ComparisonResult, AnalysisResult, HistorySummary } from '../types';
import { compareUrls, compareHistoryItems } from '../api';

interface ComparisonViewProps {
  history: HistorySummary[];
  onInspectTarget?: (result: AnalysisResult) => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({ history, onInspectTarget }) => {
  const [urlA, setUrlA] = useState('');
  const [urlB, setUrlB] = useState('');
  const [sampleLimit, setSampleLimit] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlA.trim() || !urlB.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await compareUrls(urlA.trim(), urlB.trim(), sampleLimit);
      setComparison(result);
    } catch (err: any) {
      setError(err.message || 'Comparison failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistoryPair = async (idA: string, idB: string) => {
    if (!idA || !idB || idA === idB) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await compareHistoryItems(idA, idB);
      setComparison(result);
      setUrlA(result.target_a.url);
      setUrlB(result.target_b.url);
    } catch (err: any) {
      setError(err.message || 'Failed to compare historical items');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="comparison-container">
      {/* Comparison Input Card */}
      <div className="glass-card analyzer-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <ArrowLeftRight size={20} color="var(--accent-blue)" />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Head-to-Head Target Benchmark</h3>
        </div>

        <form onSubmit={handleCompare}>
          <div className="compare-inputs-grid">
            {/* Target A URL */}
            <div className="compare-input-group">
              <label htmlFor="input-url-a" className="compare-label">Target A (First URL):</label>
              <input
                id="input-url-a"
                type="text"
                className="url-input"
                placeholder="YouTube or X.com URL..."
                value={urlA}
                onChange={(e) => setUrlA(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>

            {/* Target B URL */}
            <div className="compare-input-group">
              <label htmlFor="input-url-b" className="compare-label">Target B (Second URL):</label>
              <input
                id="input-url-b"
                type="text"
                className="url-input"
                placeholder="YouTube or X.com URL..."
                value={urlB}
                onChange={(e) => setUrlB(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', flexWrap: 'wrap', gap: '12px' }}>
            {/* Sample Limit */}
            <div className="sample-limit-row" style={{ margin: 0 }}>
              <span>Sample Limit:</span>
              <div className="limit-pills">
                {[50, 100, 200].map((limit) => (
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

            {/* Submit Button */}
            <button
              id="btn-compare-submit"
              type="submit"
              className="analyze-button"
              disabled={isLoading || !urlA.trim() || !urlB.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Benchmarking Both Targets...</span>
                </>
              ) : (
                <>
                  <ArrowLeftRight size={16} />
                  <span>Compare Head-to-Head</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Quick History Compare Helper */}
        {history.length >= 2 && (
          <div className="history-quick-compare">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 600 }}>
              Quick Benchmark from Recent History:
            </span>
            <button
              type="button"
              className="quick-compare-pill-btn"
              onClick={() => handleSelectHistoryPair(history[0].id, history[1].id)}
              disabled={isLoading}
            >
              Compare "{history[0].target_id}" vs "{history[1].target_id}"
            </button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="alert-banner error" role="alert" style={{ marginTop: '16px' }}>
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <div>
              <strong>Benchmark Failed: </strong>
              <span>{error}</span>
            </div>
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="comparison-results-wrapper">
          {/* Executive Comparative Statement */}
          <div className="comparison-headline-banner">
            <Trophy size={20} color="#fbbf24" style={{ flexShrink: 0 }} />
            <div className="comparison-headline-text">
              <span className="comparison-headline-tag">Executive Benchmark Verdict</span>
              <p>{comparison.summary_headline}</p>
            </div>
          </div>

          {/* Side-by-Side Target Columns */}
          <div className="comparison-cards-grid">
            {/* Target A Card */}
            <div className={`compare-card ${comparison.higher_positive_target === comparison.target_a.target_id ? 'winner-card' : ''}`}>
              <div className="compare-card-header">
                <span className="target-col-label">Target A</span>
                {comparison.higher_positive_target === comparison.target_a.target_id && (
                  <span className="winner-pill">
                    <Trophy size={12} /> Higher Positive (+{comparison.sentiment_delta_positive}%)
                  </span>
                )}
              </div>

              {comparison.target_a.thumbnail_url && (
                <img
                  src={comparison.target_a.thumbnail_url}
                  alt={comparison.target_a.title || 'Thumbnail'}
                  className="compare-thumb"
                />
              )}

              <h4 className="compare-target-title" title={comparison.target_a.title || ''}>
                {comparison.target_a.title || comparison.target_a.target_id}
              </h4>
              <div className="compare-target-meta">
                <span>By: <strong>{comparison.target_a.author}</strong></span>
                <span>Platform: <strong>{comparison.target_a.platform.toUpperCase()}</strong></span>
              </div>

              {/* Progress Bar */}
              <div className="sentiment-bar-track" style={{ margin: '14px 0 8px 0' }}>
                <div
                  className="sentiment-bar-segment segment-positive"
                  style={{ width: `${comparison.target_a.sentiment.positive_percentage}%` }}
                />
                <div
                  className="sentiment-bar-segment segment-neutral"
                  style={{ width: `${comparison.target_a.sentiment.neutral_percentage}%` }}
                />
                <div
                  className="sentiment-bar-segment segment-negative"
                  style={{ width: `${comparison.target_a.sentiment.negative_percentage}%` }}
                />
              </div>

              {/* Sentiment Stats Trio */}
              <div className="compare-stats-row">
                <div className="compare-stat-item text-emerald">
                  <span>Positive</span>
                  <strong>{comparison.target_a.sentiment.positive_percentage}%</strong>
                </div>
                <div className="compare-stat-item text-muted">
                  <span>Neutral</span>
                  <strong>{comparison.target_a.sentiment.neutral_percentage}%</strong>
                </div>
                <div className="compare-stat-item text-rose">
                  <span>Negative</span>
                  <strong>{comparison.target_a.sentiment.negative_percentage}%</strong>
                </div>
              </div>

              {/* Engagement Stats */}
              <div className="compare-metrics-list">
                {comparison.target_a.engagement.views && (
                  <div className="compare-metric-row">
                    <span><Eye size={13} /> Views:</span>
                    <strong>{comparison.target_a.engagement.views.toLocaleString()}</strong>
                  </div>
                )}
                {comparison.target_a.engagement.likes && (
                  <div className="compare-metric-row">
                    <span><Heart size={13} /> Likes:</span>
                    <strong>{comparison.target_a.engagement.likes.toLocaleString()}</strong>
                  </div>
                )}
                {comparison.target_a.engagement.third_party_dislikes?.estimated_dislikes && (
                  <div className="compare-metric-row text-amber">
                    <span><ThumbsDown size={13} /> Est. Dislikes:</span>
                    <strong>{comparison.target_a.engagement.third_party_dislikes.estimated_dislikes.toLocaleString()}</strong>
                  </div>
                )}
                <div className="compare-metric-row">
                  <span><Flame size={13} /> Controversy:</span>
                  <strong>{comparison.target_a.sentiment.verdict?.controversy_index || 0}/100</strong>
                </div>
              </div>

              {onInspectTarget && (
                <button
                  type="button"
                  className="inspect-target-btn"
                  onClick={() => onInspectTarget(comparison.target_a)}
                >
                  Inspect Full Target A Analysis →
                </button>
              )}
            </div>

            {/* Target B Card */}
            <div className={`compare-card ${comparison.higher_positive_target === comparison.target_b.target_id ? 'winner-card' : ''}`}>
              <div className="compare-card-header">
                <span className="target-col-label">Target B</span>
                {comparison.higher_positive_target === comparison.target_b.target_id && (
                  <span className="winner-pill">
                    <Trophy size={12} /> Higher Positive (+{Math.abs(comparison.sentiment_delta_positive)}%)
                  </span>
                )}
              </div>

              {comparison.target_b.thumbnail_url && (
                <img
                  src={comparison.target_b.thumbnail_url}
                  alt={comparison.target_b.title || 'Thumbnail'}
                  className="compare-thumb"
                />
              )}

              <h4 className="compare-target-title" title={comparison.target_b.title || ''}>
                {comparison.target_b.title || comparison.target_b.target_id}
              </h4>
              <div className="compare-target-meta">
                <span>By: <strong>{comparison.target_b.author}</strong></span>
                <span>Platform: <strong>{comparison.target_b.platform.toUpperCase()}</strong></span>
              </div>

              {/* Progress Bar */}
              <div className="sentiment-bar-track" style={{ margin: '14px 0 8px 0' }}>
                <div
                  className="sentiment-bar-segment segment-positive"
                  style={{ width: `${comparison.target_b.sentiment.positive_percentage}%` }}
                />
                <div
                  className="sentiment-bar-segment segment-neutral"
                  style={{ width: `${comparison.target_b.sentiment.neutral_percentage}%` }}
                />
                <div
                  className="sentiment-bar-segment segment-negative"
                  style={{ width: `${comparison.target_b.sentiment.negative_percentage}%` }}
                />
              </div>

              {/* Sentiment Stats Trio */}
              <div className="compare-stats-row">
                <div className="compare-stat-item text-emerald">
                  <span>Positive</span>
                  <strong>{comparison.target_b.sentiment.positive_percentage}%</strong>
                </div>
                <div className="compare-stat-item text-muted">
                  <span>Neutral</span>
                  <strong>{comparison.target_b.sentiment.neutral_percentage}%</strong>
                </div>
                <div className="compare-stat-item text-rose">
                  <span>Negative</span>
                  <strong>{comparison.target_b.sentiment.negative_percentage}%</strong>
                </div>
              </div>

              {/* Engagement Stats */}
              <div className="compare-metrics-list">
                {comparison.target_b.engagement.views && (
                  <div className="compare-metric-row">
                    <span><Eye size={13} /> Views:</span>
                    <strong>{comparison.target_b.engagement.views.toLocaleString()}</strong>
                  </div>
                )}
                {comparison.target_b.engagement.likes && (
                  <div className="compare-metric-row">
                    <span><Heart size={13} /> Likes:</span>
                    <strong>{comparison.target_b.engagement.likes.toLocaleString()}</strong>
                  </div>
                )}
                {comparison.target_b.engagement.third_party_dislikes?.estimated_dislikes && (
                  <div className="compare-metric-row text-amber">
                    <span><ThumbsDown size={13} /> Est. Dislikes:</span>
                    <strong>{comparison.target_b.engagement.third_party_dislikes.estimated_dislikes.toLocaleString()}</strong>
                  </div>
                )}
                <div className="compare-metric-row">
                  <span><Flame size={13} /> Controversy:</span>
                  <strong>{comparison.target_b.sentiment.verdict?.controversy_index || 0}/100</strong>
                </div>
              </div>

              {onInspectTarget && (
                <button
                  type="button"
                  className="inspect-target-btn"
                  onClick={() => onInspectTarget(comparison.target_b)}
                >
                  Inspect Full Target B Analysis →
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

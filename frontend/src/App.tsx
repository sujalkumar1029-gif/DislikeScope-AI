import React, { useState, useEffect } from 'react';
import { Search, ArrowLeftRight, RefreshCw } from 'lucide-react';
import { Header } from './components/Header';
import { UrlInput } from './components/UrlInput';
import { SentimentSummary } from './components/SentimentSummary';
import { EngagementMetrics } from './components/EngagementMetrics';
import { DiagnosticsCard } from './components/DiagnosticsCard';
import { CommentsList } from './components/CommentsList';
import { HistoryPanel } from './components/HistoryPanel';
import { ExportButtons } from './components/ExportButtons';
import { LimitationsNotice } from './components/LimitationsNotice';
import { ComparisonView } from './components/ComparisonView';
import type {
  PlatformType,
  AnalysisResult,
  HistorySummary as HistorySummaryType,
} from './types';
import {
  analyzeYouTube,
  analyzeX,
  fetchHistory,
  fetchHistoryItem,
  deleteHistoryItem,
} from './api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'compare'>('single');
  const [platform, setPlatform] = useState<PlatformType>('youtube');
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [selectedDriverKeyword, setSelectedDriverKeyword] = useState<string>('');
  const [history, setHistory] = useState<HistorySummaryType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Phase 2: X.com integration is fully active
  const isXAvailable = true;

  const loadHistory = async () => {
    try {
      const items = await fetchHistory();
      setHistory(items);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleAnalyze = async (url: string, sampleLimit: number) => {
    setIsLoading(true);
    setError(null);
    setSelectedDriverKeyword('');

    try {
      let result: AnalysisResult;
      if (platform === 'youtube') {
        result = await analyzeYouTube(url, sampleLimit);
      } else {
        result = await analyzeX(url, sampleLimit);
      }
      setCurrentAnalysis(result);
      await loadHistory();
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistory = async (id: string) => {
    try {
      setIsLoading(true);
      setError(null);
      setSelectedDriverKeyword('');
      const result = await fetchHistoryItem(id);
      setCurrentAnalysis(result);
      setPlatform(result.platform);
      setActiveTab('single');
    } catch (err: any) {
      setError(err.message || 'Failed to load historical report');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteHistory = async (id: string) => {
    try {
      await deleteHistoryItem(id);
      if (currentAnalysis?.id === id) {
        setCurrentAnalysis(null);
      }
      await loadHistory();
    } catch (err: any) {
      setError(err.message || 'Failed to delete report');
    }
  };

  const handleComparePairFromHistory = (_idA: string, _idB: string) => {
    setActiveTab('compare');
  };

  return (
    <div className="app-container">
      <Header />

      {/* Main Mode Navigation Bar */}
      <div className="app-mode-nav">
        <button
          type="button"
          className={`mode-tab-btn ${activeTab === 'single' ? 'active' : ''}`}
          onClick={() => setActiveTab('single')}
        >
          <Search size={16} />
          <span>Deep Target Diagnostics</span>
        </button>

        <button
          type="button"
          className={`mode-tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
          onClick={() => setActiveTab('compare')}
        >
          <ArrowLeftRight size={16} />
          <span>Head-to-Head Benchmark</span>
        </button>
      </div>

      <main className="dashboard-grid">
        <section className="main-content">
          {activeTab === 'single' ? (
            <>
              <UrlInput
                selectedPlatform={platform}
                onPlatformChange={setPlatform}
                onAnalyze={handleAnalyze}
                isLoading={isLoading}
                error={error}
                isXAvailable={isXAvailable}
              />

              {currentAnalysis && (
                <div className="glass-card" style={{ marginBottom: '28px' }}>
                  {/* Target Preview */}
                  <div className="target-preview-card">
                    {currentAnalysis.thumbnail_url && (
                      <img
                        src={currentAnalysis.thumbnail_url}
                        alt={currentAnalysis.title || 'Video Thumbnail'}
                        className="target-thumbnail"
                      />
                    )}
                    <div className="target-details">
                      <h2 className="target-title" title={currentAnalysis.title || ''}>
                        {currentAnalysis.title}
                      </h2>
                      <div className="target-meta">
                        <span>Creator: <strong>{currentAnalysis.author}</strong></span>
                        <span>Platform: <strong>{currentAnalysis.platform.toUpperCase()}</strong></span>
                        <span>Analyzed: {new Date(currentAnalysis.created_at).toLocaleString()}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', marginTop: '10px' }}>
                        <ExportButtons analysisId={currentAnalysis.id} result={currentAnalysis} />
                        <button
                          type="button"
                          className="export-btn"
                          onClick={() => handleAnalyze(currentAnalysis.url, 100)}
                          disabled={isLoading}
                          title="Re-run extraction and update analysis fresh"
                        >
                          <RefreshCw size={15} color="#3b82f6" className={isLoading ? 'animate-spin' : ''} />
                          <span>Re-analyze</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Sentiment Summary with Verdict, Drivers, Resonance & Distribution */}
                  <SentimentSummary
                    summary={currentAnalysis.sentiment}
                    methodology={currentAnalysis.methodology}
                    selectedKeyword={selectedDriverKeyword}
                    onSelectKeyword={setSelectedDriverKeyword}
                  />

                  {/* Engagement Metrics (Separated from Sentiment) */}
                  <EngagementMetrics metrics={currentAnalysis.engagement} />

                  {/* Retrieval Diagnostics */}
                  <DiagnosticsCard diagnostics={currentAnalysis.diagnostics} />

                  {/* Interactive Comment Explorer */}
                  <CommentsList
                    comments={currentAnalysis.comments_sample}
                    selectedKeyword={selectedDriverKeyword}
                    onClearKeyword={() => setSelectedDriverKeyword('')}
                  />
                </div>
              )}

              <LimitationsNotice />
            </>
          ) : (
            <ComparisonView
              history={history}
              onInspectTarget={(target) => {
                setCurrentAnalysis(target);
                setPlatform(target.platform);
                setActiveTab('single');
              }}
            />
          )}
        </section>

        {/* Sidebar History Panel */}
        <aside>
          <div className="glass-card">
            <HistoryPanel
              history={history}
              selectedId={currentAnalysis?.id || null}
              onSelect={handleSelectHistory}
              onDelete={handleDeleteHistory}
              onComparePair={handleComparePairFromHistory}
            />
          </div>
        </aside>
      </main>
    </div>
  );
};

export default App;


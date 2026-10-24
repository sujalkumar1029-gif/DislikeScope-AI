import React from 'react';
import { History, Trash2, Clock } from 'lucide-react';
import { YouTubeIcon } from './Icons';
import type { HistorySummary } from '../types';

interface HistoryPanelProps {
  history: HistorySummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onComparePair?: (idA: string, idB: string) => void;
}

export const HistoryPanel: React.FC<HistoryPanelProps> = ({
  history,
  selectedId,
  onSelect,
  onDelete,
  onComparePair,
}) => {
  const [selectedForCompare, setSelectedForCompare] = React.useState<string[]>([]);

  const toggleCompareSelect = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedForCompare((prev) => {
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }
      if (prev.length >= 2) {
        return [prev[1], id];
      }
      return [...prev, id];
    });
  };

  const handleTriggerCompare = () => {
    if (selectedForCompare.length === 2 && onComparePair) {
      onComparePair(selectedForCompare[0], selectedForCompare[1]);
      setSelectedForCompare([]);
    }
  };

  return (
    <div className="history-panel">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <History size={18} color="#3b82f6" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Analysis History</h3>
        </div>

        {onComparePair && selectedForCompare.length === 2 && (
          <button
            type="button"
            className="history-compare-action-btn"
            onClick={handleTriggerCompare}
            title="Benchmark these two reports head-to-head"
          >
            Compare (2)
          </button>
        )}
      </div>

      {history.length >= 2 && onComparePair && selectedForCompare.length < 2 && (
        <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '8px' }}>
          Select any 2 items to compare side-by-side
        </div>
      )}

      {history.length === 0 ? (
        <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
          No local analysis history yet. Past reports will be stored here.
        </div>
      ) : (
        history.map((item) => {
          const isCompareSelected = selectedForCompare.includes(item.id);
          return (
            <div
              key={item.id}
              className={`history-item-card ${selectedId === item.id ? 'selected' : ''} ${isCompareSelected ? 'compare-picked' : ''}`}
              onClick={() => onSelect(item.id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {item.platform === 'youtube' ? (
                    <YouTubeIcon size={14} color="#ff0033" />
                  ) : (
                    <span style={{ fontWeight: 800, fontSize: '0.8rem' }}>𝕏</span>
                  )}
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {item.target_id}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {onComparePair && (
                    <button
                      type="button"
                      className={`compare-select-btn ${isCompareSelected ? 'active' : ''}`}
                      title={isCompareSelected ? 'Remove from compare' : 'Select for comparison'}
                      onClick={(e) => toggleCompareSelect(item.id, e)}
                    >
                      {isCompareSelected ? '✓ Picked' : '+ Compare'}
                    </button>
                  )}
                  <button
                    type="button"
                    className="delete-btn"
                    title="Delete this analysis report"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(item.id);
                    }}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>


            <div className="history-item-title" title={item.title || item.target_id}>
              {item.title || item.target_id}
            </div>

            <div className="history-item-meta">
              <div className="history-counts">
                <span className="count-pos">+{item.positive_count}</span>
                <span className="count-neu">~{item.neutral_count}</span>
                <span className="count-neg">-{item.negative_count}</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={11} />
                <span>
                  {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          </div>
        );
      })
    )}
  </div>
);
};

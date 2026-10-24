import React from 'react';
import { Sparkles, ThumbsDown, MessageSquare } from 'lucide-react';
import type { SentimentDriverItem } from '../types';

interface SentimentDriversProps {
  praiseDrivers: SentimentDriverItem[];
  dislikeDrivers: SentimentDriverItem[];
  selectedKeyword?: string;
  onSelectKeyword?: (keyword: string) => void;
}

export const SentimentDrivers: React.FC<SentimentDriversProps> = ({
  praiseDrivers,
  dislikeDrivers,
  selectedKeyword,
  onSelectKeyword,
}) => {
  const hasPraise = praiseDrivers && praiseDrivers.length > 0;
  const hasDislike = dislikeDrivers && dislikeDrivers.length > 0;

  if (!hasPraise && !hasDislike) return null;

  return (
    <div className="sentiment-drivers-container">
      <div className="drivers-grid">
        {/* Praise Drivers */}
        <div className="drivers-card praise-card">
          <div className="drivers-card-header">
            <div className="drivers-card-title text-emerald">
              <Sparkles size={16} />
              <span>Top Praise Drivers (Key Themes)</span>
            </div>
            <span className="drivers-hint">Click keyword to filter comments</span>
          </div>

          <div className="driver-pills-list">
            {hasPraise ? (
              praiseDrivers.map((item) => {
                const isSelected = selectedKeyword?.toLowerCase() === item.keyword.toLowerCase();
                return (
                  <button
                    key={item.keyword}
                    type="button"
                    className={`driver-pill praise-pill ${isSelected ? 'selected' : ''}`}
                    onClick={() => onSelectKeyword && onSelectKeyword(item.keyword)}
                    title={item.sample_snippet ? `"${item.sample_snippet}"` : undefined}
                  >
                    <span className="driver-keyword">{item.keyword}</span>
                    <span className="driver-count">{item.count}</span>
                  </button>
                );
              })
            ) : (
              <span className="no-drivers-text">No recurring positive themes identified</span>
            )}
          </div>
        </div>

        {/* Dislike Drivers */}
        <div className="drivers-card dislike-card">
          <div className="drivers-card-header">
            <div className="drivers-card-title text-rose">
              <ThumbsDown size={16} />
              <span>Top Dislike Drivers (Audience Criticisms)</span>
            </div>
            <span className="drivers-hint">Click keyword to filter comments</span>
          </div>

          <div className="driver-pills-list">
            {hasDislike ? (
              dislikeDrivers.map((item) => {
                const isSelected = selectedKeyword?.toLowerCase() === item.keyword.toLowerCase();
                return (
                  <button
                    key={item.keyword}
                    type="button"
                    className={`driver-pill dislike-pill ${isSelected ? 'selected' : ''}`}
                    onClick={() => onSelectKeyword && onSelectKeyword(item.keyword)}
                    title={item.sample_snippet ? `"${item.sample_snippet}"` : undefined}
                  >
                    <span className="driver-keyword">{item.keyword}</span>
                    <span className="driver-count">{item.count}</span>
                  </button>
                );
              })
            ) : (
              <span className="no-drivers-text">No recurring critical complaints identified</span>
            )}
          </div>
        </div>
      </div>

      {selectedKeyword && (
        <div className="active-driver-filter-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageSquare size={14} color="var(--accent-cyan)" />
            <span>Filtering comments by topic: <strong>"{selectedKeyword}"</strong></span>
          </div>
          <button
            type="button"
            className="clear-driver-filter-btn"
            onClick={() => onSelectKeyword && onSelectKeyword('')}
          >
            Clear Filter
          </button>
        </div>
      )}
    </div>
  );
};

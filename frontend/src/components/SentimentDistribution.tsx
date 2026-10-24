import React from 'react';
import { BarChart2 } from 'lucide-react';
import type { ScoreBucket } from '../types';

interface SentimentDistributionProps {
  distribution: ScoreBucket[];
}

export const SentimentDistribution: React.FC<SentimentDistributionProps> = ({ distribution }) => {
  if (!distribution || distribution.length === 0) return null;

  const getBucketColorClass = (index: number) => {
    switch (index) {
      case 0:
        return 'bucket-very-neg';
      case 1:
        return 'bucket-leaning-neg';
      case 2:
        return 'bucket-neutral';
      case 3:
        return 'bucket-leaning-pos';
      case 4:
        return 'bucket-very-pos';
      default:
        return 'bucket-neutral';
    }
  };

  return (
    <div className="distribution-container">
      <div className="section-subtitle-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart2 size={16} color="var(--accent-cyan)" />
          <h4 className="subsection-title">Score Polarity Distribution (5-Tier Histogram)</h4>
        </div>
        <span className="text-dim-small">Spread across -1.0 (Critical) to +1.0 (Praise)</span>
      </div>

      <div className="histogram-grid">
        {distribution.map((bucket, idx) => (
          <div key={bucket.label} className="histogram-column">
            <div className="histogram-bar-track">
              <div
                className={`histogram-bar-fill ${getBucketColorClass(idx)}`}
                style={{ height: `${Math.max(bucket.percentage, 4)}%` }}
                title={`${bucket.label} (${bucket.range_label}): ${bucket.count} comments (${bucket.percentage}%)`}
              />
            </div>
            <div className="histogram-label-row">
              <span className="histogram-count">{bucket.count}</span>
              <span className="histogram-pct">{bucket.percentage}%</span>
            </div>
            <div className="histogram-name" title={bucket.range_label}>
              {bucket.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

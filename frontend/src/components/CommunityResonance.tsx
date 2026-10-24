import React from 'react';
import { ThumbsUp, Scale, Info } from 'lucide-react';
import type { LikeWeightedMetrics, SentimentSummary as SentimentSummaryType } from '../types';

interface CommunityResonanceProps {
  summary: SentimentSummaryType;
  likeWeighted?: LikeWeightedMetrics;
}

export const CommunityResonance: React.FC<CommunityResonanceProps> = ({ summary, likeWeighted }) => {
  if (!likeWeighted || likeWeighted.total_weight === 0) return null;

  const rawPos = summary.positive_percentage;
  const rawNeg = summary.negative_percentage;
  const wPos = likeWeighted.weighted_positive_pct;
  const wNeg = likeWeighted.weighted_negative_pct;

  const posDelta = roundDelta(wPos - rawPos);
  const negDelta = roundDelta(wNeg - rawNeg);

  function roundDelta(val: number): number {
    return Math.round(val * 10) / 10;
  }

  return (
    <div className="resonance-container">
      <div className="section-subtitle-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Scale size={16} color="var(--accent-blue)" />
          <h4 className="subsection-title">Community Resonance (Like-Weighted Sentiment)</h4>
        </div>
        <span className="text-dim-small" title="Weighted by community upvotes per comment">
          Compares raw comment frequency against total upvote weight ({likeWeighted.total_weight.toLocaleString()} total upvote weight)
        </span>
      </div>

      <div className="resonance-comparison-grid">
        {/* Raw Sentiment Column */}
        <div className="resonance-col">
          <div className="resonance-col-title">
            <span>Raw Frequency (Per Comment)</span>
          </div>
          <div className="resonance-stats">
            <div className="resonance-stat-row text-emerald">
              <span>Positive:</span>
              <strong>{rawPos}%</strong>
            </div>
            <div className="resonance-stat-row text-rose">
              <span>Negative:</span>
              <strong>{rawNeg}%</strong>
            </div>
            <div className="resonance-stat-row text-muted">
              <span>Mean Compound:</span>
              <strong>{summary.average_compound > 0 ? `+${summary.average_compound}` : summary.average_compound}</strong>
            </div>
          </div>
        </div>

        {/* Like-Weighted Column */}
        <div className="resonance-col weighted-col">
          <div className="resonance-col-title">
            <ThumbsUp size={13} color="var(--accent-cyan)" />
            <span>Like-Weighted (Community Resonance)</span>
          </div>
          <div className="resonance-stats">
            <div className="resonance-stat-row text-emerald">
              <span>Positive:</span>
              <strong>{wPos}%</strong>
              <span className={`delta-tag ${posDelta >= 0 ? 'pos' : 'neg'}`}>
                {posDelta >= 0 ? `+${posDelta}%` : `${posDelta}%`}
              </span>
            </div>
            <div className="resonance-stat-row text-rose">
              <span>Negative:</span>
              <strong>{wNeg}%</strong>
              <span className={`delta-tag ${negDelta <= 0 ? 'pos' : 'neg'}`}>
                {negDelta >= 0 ? `+${negDelta}%` : `${negDelta}%`}
              </span>
            </div>
            <div className="resonance-stat-row text-muted">
              <span>Weighted Compound:</span>
              <strong>{likeWeighted.weighted_compound > 0 ? `+${likeWeighted.weighted_compound}` : likeWeighted.weighted_compound}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="resonance-note">
        <Info size={14} className="resonance-note-icon" />
        <span>
          {wPos > rawPos
            ? 'Community likes heavily amplify positive feedback, indicating that critical comments have lower community consensus.'
            : wNeg > rawNeg
            ? 'Critical feedback received higher-than-average community likes, amplifying audience dissatisfaction.'
            : 'Community upvotes are evenly distributed across positive and critical comments.'}
        </span>
      </div>
    </div>
  );
};

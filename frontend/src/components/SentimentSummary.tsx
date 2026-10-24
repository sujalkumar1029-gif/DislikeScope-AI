import React from 'react';
import { ThumbsUp, Minus, ThumbsDown, BarChart3, Info } from 'lucide-react';
import type { SentimentSummary as SentimentSummaryType } from '../types';
import { VerdictBanner } from './VerdictBanner';
import { SentimentDistribution } from './SentimentDistribution';
import { SentimentDrivers } from './SentimentDrivers';
import { CommunityResonance } from './CommunityResonance';

interface SentimentSummaryProps {
  summary: SentimentSummaryType;
  methodology: string;
  selectedKeyword?: string;
  onSelectKeyword?: (keyword: string) => void;
}

export const SentimentSummary: React.FC<SentimentSummaryProps> = ({
  summary,
  methodology,
  selectedKeyword,
  onSelectKeyword,
}) => {
  const {
    positive_count,
    neutral_count,
    negative_count,
    total_analyzed,
    positive_percentage,
    neutral_percentage,
    negative_percentage,
    average_compound,
    dislike_drivers = [],
    praise_drivers = [],
    score_distribution = [],
    like_weighted,
    verdict,
  } = summary;

  if (total_analyzed === 0) {
    return (
      <div className="sentiment-section">
        {verdict && <VerdictBanner verdict={verdict} />}
        <h3 className="section-title" style={{ marginTop: '16px' }}>
          <BarChart3 size={18} color="#06b6d4" />
          <span>Audience Sentiment Analysis</span>
        </h3>
        <div className="alert-banner warning">
          <Info size={18} />
          <div>
            <strong>No sentiment data available: </strong>
            <span>Zero comments were retrieved or analyzed. Metrics are not fabricated.</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="sentiment-section">
      {/* 1. Executive Diagnostic Verdict Banner */}
      {verdict && <VerdictBanner verdict={verdict} />}

      <h3 className="section-title" style={{ marginTop: verdict ? '20px' : '0' }}>
        <BarChart3 size={18} color="#06b6d4" />
        <span>Audience Sentiment Breakdown ({total_analyzed} comments analyzed)</span>
      </h3>

      {/* 2. Trio Metric Cards */}
      <div className="cards-trio">
        <div className="metric-card positive">
          <div className="metric-header">
            <span>Positive</span>
            <ThumbsUp size={16} color="var(--sentiment-pos)" />
          </div>
          <div className="metric-value">{positive_count}</div>
          <div className="metric-percentage">{positive_percentage}% of analyzed</div>
        </div>

        <div className="metric-card neutral">
          <div className="metric-header">
            <span>Neutral</span>
            <Minus size={16} color="var(--sentiment-neu)" />
          </div>
          <div className="metric-value">{neutral_count}</div>
          <div className="metric-percentage">{neutral_percentage}% of analyzed</div>
        </div>

        <div className="metric-card negative">
          <div className="metric-header">
            <span>Negative</span>
            <ThumbsDown size={16} color="var(--sentiment-neg)" />
          </div>
          <div className="metric-value">{negative_count}</div>
          <div className="metric-percentage">{negative_percentage}% of analyzed</div>
        </div>
      </div>

      {/* 3. Visual Stacked Progress Bar */}
      <div className="sentiment-bar-wrapper">
        <div className="sentiment-bar-track" title={`Positive: ${positive_percentage}%, Neutral: ${neutral_percentage}%, Negative: ${negative_percentage}%`}>
          <div
            className="sentiment-bar-segment segment-positive"
            style={{ width: `${positive_percentage}%` }}
          />
          <div
            className="sentiment-bar-segment segment-neutral"
            style={{ width: `${neutral_percentage}%` }}
          />
          <div
            className="sentiment-bar-segment segment-negative"
            style={{ width: `${negative_percentage}%` }}
          />
        </div>
      </div>

      {/* 4. Community Resonance (Like-Weighted Sentiment vs Raw) */}
      {like_weighted && (
        <CommunityResonance summary={summary} likeWeighted={like_weighted} />
      )}

      {/* 5. Key Praise & Dislike Drivers */}
      {(praise_drivers.length > 0 || dislike_drivers.length > 0) && (
        <SentimentDrivers
          praiseDrivers={praise_drivers}
          dislikeDrivers={dislike_drivers}
          selectedKeyword={selectedKeyword}
          onSelectKeyword={onSelectKeyword}
        />
      )}

      {/* 6. Score Polarity Distribution Histogram */}
      {score_distribution.length > 0 && (
        <SentimentDistribution distribution={score_distribution} />
      )}

      {/* 7. Methodology & Compound Score */}
      <div className="methodology-box">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontWeight: 600 }}>
          <span>Methodology & Thresholding</span>
          <span>Mean Compound Score: {average_compound > 0 ? `+${average_compound}` : average_compound}</span>
        </div>
        <div>{methodology}</div>
      </div>
    </div>
  );
};


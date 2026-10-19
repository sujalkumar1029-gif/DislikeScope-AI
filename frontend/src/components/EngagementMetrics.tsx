import React from 'react';
import { Eye, Heart, MessageSquare, ThumbsDown, Share2, HelpCircle } from 'lucide-react';
import type { EngagementMetrics as EngagementMetricsType } from '../types';

interface EngagementMetricsProps {
  metrics: EngagementMetricsType;
}

export const EngagementMetrics: React.FC<EngagementMetricsProps> = ({ metrics }) => {
  const { views, likes, comments, reposts, quotes, third_party_dislikes } = metrics;

  return (
    <div>
      <h3 className="section-title">
        <Eye size={18} color="#3b82f6" />
        <span>Platform Engagement Metrics (Independent of Sentiment)</span>
      </h3>

      <div className="engagement-grid">
        {views !== null && views !== undefined && (
          <div className="engagement-card">
            <div className="engagement-label">
              <Eye size={14} />
              <span>Total Views</span>
            </div>
            <div className="engagement-val">{views.toLocaleString()}</div>
          </div>
        )}

        {likes !== null && likes !== undefined && (
          <div className="engagement-card">
            <div className="engagement-label">
              <Heart size={14} />
              <span>Public Likes</span>
            </div>
            <div className="engagement-val">{likes.toLocaleString()}</div>
          </div>
        )}

        {comments !== null && comments !== undefined && (
          <div className="engagement-card">
            <div className="engagement-label">
              <MessageSquare size={14} />
              <span>Reported Comments</span>
            </div>
            <div className="engagement-val">{comments.toLocaleString()}</div>
          </div>
        )}

        {reposts !== null && reposts !== undefined && (
          <div className="engagement-card">
            <div className="engagement-label">
              <Share2 size={14} />
              <span>Reposts</span>
            </div>
            <div className="engagement-val">{reposts.toLocaleString()}</div>
          </div>
        )}

        {quotes !== null && quotes !== undefined && (
          <div className="engagement-card">
            <div className="engagement-label">
              <MessageSquare size={14} />
              <span>Quotes</span>
            </div>
            <div className="engagement-val">{quotes.toLocaleString()}</div>
          </div>
        )}

        {/* Third-Party Estimated Dislikes (YouTube) */}
        {third_party_dislikes && (
          <div className="engagement-card" style={{ borderColor: 'rgba(245, 158, 11, 0.4)' }}>
            <div className="engagement-label" style={{ color: '#fbbf24' }}>
              <ThumbsDown size={14} />
              <span>Est. Dislikes (3rd-Party)</span>
              <span title={third_party_dislikes.limitations_note}>
                <HelpCircle size={12} style={{ cursor: 'help' }} />
              </span>
            </div>
            <div className="engagement-val" style={{ color: '#fbbf24' }}>
              {third_party_dislikes.estimated_dislikes !== null && third_party_dislikes.estimated_dislikes !== undefined
                ? third_party_dislikes.estimated_dislikes.toLocaleString()
                : 'Unavailable'}
            </div>
            <div className="dislike-estimate-tag">
              Estimate: {third_party_dislikes.source}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

import React from 'react';
import { AlertCircle } from 'lucide-react';

export const LimitationsNotice: React.FC = () => {
  return (
    <div className="limitations-section">
      <div className="limitations-title">
        <AlertCircle size={18} color="#f59e0b" />
        <span>Platform Access Boundaries & Truth Policy</span>
      </div>
      <div className="limitations-content">
        <p style={{ marginBottom: '8px' }}>
          <strong>YouTube:</strong> Extraction processes accessible public comment threads without API keys. If a creator has explicitly turned off comments, or if the video is private/unlisted or geo-restricted, DislikeScope-AI reports zero comments rather than simulating sentiment. Dislike metrics are labeled as third-party statistical estimates from Return YouTube Dislike (RYD) archives, not official YouTube data.
        </p>
        <p>
          <strong>X.com (Phase 2):</strong> Operates exclusively within public syndication and permitted web endpoints. Due to platform login walls, reply access may be limited on private or heavily restricted accounts; engagement ratios are never treated as direct sentiment.
        </p>
      </div>
    </div>
  );
};

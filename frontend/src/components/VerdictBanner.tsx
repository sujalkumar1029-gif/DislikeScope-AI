import React from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle, Info, Flame } from 'lucide-react';
import type { DiagnosticVerdict } from '../types';

interface VerdictBannerProps {
  verdict: DiagnosticVerdict;
}

export const VerdictBanner: React.FC<VerdictBannerProps> = ({ verdict }) => {
  const { label, headline, severity, controversy_index, controversy_level } = verdict;

  const getSeverityIcon = () => {
    switch (severity) {
      case 'success':
        return <ShieldCheck size={22} className="text-emerald" />;
      case 'critical':
        return <AlertCircle size={22} className="text-rose" />;
      case 'warning':
        return <AlertTriangle size={22} className="text-amber" />;
      case 'info':
      default:
        return <Info size={22} className="text-cyan" />;
    }
  };

  const getControversyBadgeClass = () => {
    if (controversy_index >= 75) return 'badge-intense';
    if (controversy_index >= 50) return 'badge-elevated';
    if (controversy_index >= 25) return 'badge-moderate';
    return 'badge-consensus';
  };

  return (
    <div className={`verdict-banner-container severity-${severity}`}>
      <div className="verdict-banner-content">
        <div className="verdict-icon-wrapper">
          {getSeverityIcon()}
        </div>

        <div className="verdict-text-block">
          <div className="verdict-header-row">
            <span className="verdict-badge">Executive Verdict</span>
            <h3 className="verdict-title">{label}</h3>
          </div>
          <p className="verdict-headline">{headline}</p>
        </div>
      </div>

      <div className="verdict-controversy-card">
        <div className="controversy-header">
          <Flame size={14} className="controversy-flame-icon" />
          <span>Controversy Index</span>
        </div>
        <div className="controversy-score-row">
          <span className="controversy-score-value">{controversy_index}</span>
          <span className="controversy-score-max">/100</span>
        </div>
        <div className={`controversy-tier-pill ${getControversyBadgeClass()}`}>
          {controversy_level}
        </div>
      </div>
    </div>
  );
};

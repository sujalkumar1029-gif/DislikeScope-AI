import React from 'react';
import { ShieldCheck, Activity } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="app-header">
      <div className="brand-wrapper">
        <div className="brand-logo" aria-hidden="true">
          <Activity size={24} color="#ffffff" />
        </div>
        <div className="brand-title-group">
          <h1>DislikeScope-AI</h1>
          <p className="brand-subtitle">
            Authentic Social Sentiment & Dislike Diagnostics — Zero Fabricated Data
          </p>
        </div>
      </div>

      <div className="header-badges">
        <div className="truth-badge active-dot" title="Strict truth policy enforced: verified counts only">
          <ShieldCheck size={14} />
          <span>Truth Policy Active</span>
        </div>
      </div>
    </header>
  );
};

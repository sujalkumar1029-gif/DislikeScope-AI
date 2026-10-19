import React from 'react';
import { Database, AlertTriangle } from 'lucide-react';
import type { RetrievalDiagnostics } from '../types';

interface DiagnosticsCardProps {
  diagnostics: RetrievalDiagnostics;
}

export const DiagnosticsCard: React.FC<DiagnosticsCardProps> = ({ diagnostics }) => {
  const {
    reported_comment_count,
    retrieved_records_count,
    usable_text_count,
    analyzed_count,
    extraction_status,
    failure_reason,
    comments_disabled,
    limitations_note,
  } = diagnostics;

  return (
    <div className="diagnostics-box">
      <h3 className="section-title">
        <Database size={18} color="#a855f7" />
        <span>Retrieval & Processing Diagnostics</span>
      </h3>

      <table className="diagnostics-table">
        <tbody>
          <tr>
            <th>Platform Reported Comments</th>
            <td>{reported_comment_count !== null && reported_comment_count !== undefined ? reported_comment_count.toLocaleString() : 'Not publicly disclosed'}</td>
          </tr>
          <tr>
            <th>Raw Records Retrieved</th>
            <td>{retrieved_records_count}</td>
          </tr>
          <tr>
            <th>Usable Text Records</th>
            <td>{usable_text_count}</td>
          </tr>
          <tr>
            <th>Successfully Analyzed Items</th>
            <td>{analyzed_count}</td>
          </tr>
          <tr>
            <th>Extraction Status</th>
            <td>
              <span className={`status-pill ${extraction_status}`}>
                {extraction_status}
              </span>
            </td>
          </tr>
          {comments_disabled && (
            <tr>
              <th>Comments State</th>
              <td style={{ color: '#fbbf24' }}>Explicitly Turned Off / Disabled</td>
            </tr>
          )}
        </tbody>
      </table>

      {failure_reason && (
        <div className="alert-banner warning" style={{ marginTop: '14px' }}>
          <AlertTriangle size={18} style={{ flexShrink: 0 }} />
          <div>
            <strong>Retrieval Notice: </strong>
            <span>{failure_reason}</span>
          </div>
        </div>
      )}

      {limitations_note && (
        <div style={{ marginTop: '10px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
          * {limitations_note}
        </div>
      )}
    </div>
  );
};

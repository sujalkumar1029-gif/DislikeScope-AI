import React, { useState } from 'react';
import { FileJson, FileSpreadsheet, Copy, Check } from 'lucide-react';
import { getExportJsonUrl, getExportCsvUrl } from '../api';
import type { AnalysisResult } from '../types';

interface ExportButtonsProps {
  analysisId: string;
  result?: AnalysisResult;
}

export const ExportButtons: React.FC<ExportButtonsProps> = ({ analysisId, result }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyMarkdown = async () => {
    if (!result) return;

    const sent = result.sentiment;
    const diag = result.diagnostics;
    const verdict = sent.verdict;
    const weighted = sent.like_weighted;

    let praiseText = (sent.praise_drivers || [])
      .map((d) => `- **${d.keyword}** (${d.count} mentions)${d.sample_snippet ? `: _"${d.sample_snippet}"_` : ''}`)
      .join('\n');
    if (!praiseText) praiseText = '- _No recurring positive themes identified_';

    let dislikeText = (sent.dislike_drivers || [])
      .map((d) => `- **${d.keyword}** (${d.count} mentions)${d.sample_snippet ? `: _"${d.sample_snippet}"_` : ''}`)
      .join('\n');
    if (!dislikeText) dislikeText = '- _No recurring critical complaints identified_';

    const mdReport = `# 🔍 DislikeScope-AI Audience Diagnostics Report

### Target: [${result.title || result.target_id}](${result.url})
- **Creator / Author**: ${result.author || 'N/A'}
- **Platform**: ${result.platform.toUpperCase()}
- **Analyzed At**: ${new Date(result.created_at).toUTCString()}

---

## ⚖️ Executive Verdict
> **${verdict?.label || 'Analyzed'}**  
> ${verdict?.headline || 'Diagnostics complete.'}  
> **Controversy Index**: ${verdict?.controversy_index ?? 0}/100 (${verdict?.controversy_level || 'N/A'})

---

## 📊 Audience Sentiment Breakdown (${sent.total_analyzed} comments analyzed)
| Sentiment | Raw Count | Raw Frequency | Community Resonance (Like-Weighted) |
| :--- | :--- | :--- | :--- |
| **Positive** | ${sent.positive_count} | ${sent.positive_percentage}% | ${weighted ? `${weighted.weighted_positive_pct}%` : 'N/A'} |
| **Neutral** | ${sent.neutral_count} | ${sent.neutral_percentage}% | ${weighted ? `${weighted.weighted_neutral_pct}%` : 'N/A'} |
| **Negative** | ${sent.negative_count} | ${sent.negative_percentage}% | ${weighted ? `${weighted.weighted_negative_pct}%` : 'N/A'} |
| **Total** | ${sent.total_analyzed} | 100.0% | Mean Compound: ${sent.average_compound} |

---

## 🚀 Key Drivers
### Top Praise Themes:
${praiseText}

### Top Dislike Drivers (Criticisms):
${dislikeText}

---

## 🔒 Truth Policy Diagnostics
- **Platform Reported**: ${diag.reported_comment_count !== null && diag.reported_comment_count !== undefined ? diag.reported_comment_count.toLocaleString() : 'N/A'}
- **Retrieved Raw Records**: ${diag.retrieved_records_count}
- **Usable Text Records**: ${diag.usable_text_count}
- **Successfully Analyzed**: ${diag.analyzed_count}
- **Extraction Status**: \`${diag.extraction_status}\`
- **Methodology**: ${result.methodology}
`;

    try {
      await navigator.clipboard.writeText(mdReport);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error('Failed to copy markdown report:', err);
    }
  };

  return (
    <div className="export-group">
      {result && (
        <button
          type="button"
          id="btn-copy-markdown-report"
          className={`export-btn ${copied ? 'copied' : ''}`}
          onClick={handleCopyMarkdown}
          title="Copy formatted Markdown audit report to clipboard (ideal for Notion, Slack, GitHub)"
        >
          {copied ? <Check size={16} color="#34d399" /> : <Copy size={16} color="#a855f7" />}
          <span>{copied ? 'Copied Markdown!' : 'Copy Audit Report'}</span>
        </button>
      )}

      <a
        id="btn-export-json"
        href={getExportJsonUrl(analysisId)}
        download
        className="export-btn"
        title="Download full analysis and diagnostics as structured JSON"
      >
        <FileJson size={16} color="#06b6d4" />
        <span>Export JSON</span>
      </a>

      <a
        id="btn-export-csv"
        href={getExportCsvUrl(analysisId)}
        download
        className="export-btn"
        title="Download detailed analysis and scored comments as CSV"
      >
        <FileSpreadsheet size={16} color="#10b981" />
        <span>Export CSV</span>
      </a>
    </div>
  );
};


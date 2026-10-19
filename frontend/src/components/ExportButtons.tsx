import React from 'react';
import { FileJson, FileSpreadsheet } from 'lucide-react';
import { getExportJsonUrl, getExportCsvUrl } from '../api';

interface ExportButtonsProps {
  analysisId: string;
}

export const ExportButtons: React.FC<ExportButtonsProps> = ({ analysisId }) => {
  return (
    <div className="export-group">
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

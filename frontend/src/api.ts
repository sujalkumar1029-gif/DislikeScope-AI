import type { AnalysisResult, HistorySummary, ComparisonResult } from './types';

const API_BASE = '/api';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'An unexpected error occurred';
    try {
      const data = await res.json();
      if (data && data.detail) {
        errorDetail = data.detail;
      }
    } catch {
      errorDetail = `Request failed with status code ${res.status}`;
    }
    throw new ApiError(errorDetail, res.status);
  }
  return res.json();
}

export async function analyzeYouTube(url: string, sampleLimit: number = 100): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/youtube`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, sample_limit: sampleLimit }),
  });
  return handleResponse<AnalysisResult>(res);
}

export async function analyzeX(url: string, sampleLimit: number = 100): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/x`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, sample_limit: sampleLimit }),
  });
  return handleResponse<AnalysisResult>(res);
}

export async function compareUrls(url_a: string, url_b: string, sampleLimit: number = 100): Promise<ComparisonResult> {
  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url_a, url_b, sample_limit: sampleLimit }),
  });
  return handleResponse<ComparisonResult>(res);
}

export async function compareHistoryItems(id_a: string, id_b: string): Promise<ComparisonResult> {
  const res = await fetch(`${API_BASE}/compare?id_a=${encodeURIComponent(id_a)}&id_b=${encodeURIComponent(id_b)}`);
  return handleResponse<ComparisonResult>(res);
}

export async function fetchHistory(): Promise<HistorySummary[]> {
  const res = await fetch(`${API_BASE}/history?limit=50`);
  return handleResponse<HistorySummary[]>(res);
}

export async function fetchHistoryItem(id: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/history/${encodeURIComponent(id)}`);
  return handleResponse<AnalysisResult>(res);
}

export async function deleteHistoryItem(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/history/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
  await handleResponse<{ success: boolean }>(res);
}

export function getExportJsonUrl(id: string): string {
  return `${API_BASE}/export/${encodeURIComponent(id)}/json`;
}

export function getExportCsvUrl(id: string): string {
  return `${API_BASE}/export/${encodeURIComponent(id)}/csv`;
}


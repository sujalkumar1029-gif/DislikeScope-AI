export type PlatformType = 'youtube' | 'x';

export type SentimentCategory = 'positive' | 'neutral' | 'negative';

export interface CommentItem {
  id: string;
  author: string;
  text: string;
  likes?: number;
  published_at?: string;
  sentiment?: SentimentCategory;
  sentiment_score?: number;
  sentiment_breakdown?: {
    pos: number;
    neu: number;
    neg: number;
  };
}

export interface SentimentDriverItem {
  keyword: string;
  count: number;
  sentiment: SentimentCategory;
  sample_snippet?: string;
}

export interface ScoreBucket {
  label: string;
  range_label: string;
  count: number;
  percentage: number;
}

export interface LikeWeightedMetrics {
  weighted_compound: number;
  weighted_positive_pct: number;
  weighted_neutral_pct: number;
  weighted_negative_pct: number;
  total_weight: number;
}

export interface DiagnosticVerdict {
  label: string;
  headline: string;
  severity: 'success' | 'info' | 'warning' | 'critical';
  controversy_index: number;
  controversy_level: string;
}

export interface SentimentSummary {
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  total_analyzed: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
  average_compound: number;
  dislike_drivers?: SentimentDriverItem[];
  praise_drivers?: SentimentDriverItem[];
  score_distribution?: ScoreBucket[];
  like_weighted?: LikeWeightedMetrics;
  verdict?: DiagnosticVerdict;
}

export interface ThirdPartyDislikes {
  estimated_dislikes?: number;
  estimated_likes?: number;
  rating?: number;
  source: string;
  is_estimate: boolean;
  limitations_note: string;
}

export interface EngagementMetrics {
  views?: number;
  likes?: number;
  comments?: number;
  reposts?: number;
  quotes?: number;
  third_party_dislikes?: ThirdPartyDislikes;
}

export interface RetrievalDiagnostics {
  reported_comment_count?: number;
  retrieved_records_count: number;
  usable_text_count: number;
  analyzed_count: number;
  extraction_status: 'success' | 'partial' | 'empty' | 'disabled' | 'restricted' | 'error';
  failure_reason?: string;
  comments_disabled: boolean;
  limitations_note?: string;
}

export interface AnalysisResult {
  id: string;
  platform: PlatformType;
  url: string;
  target_id: string;
  title?: string;
  author?: string;
  thumbnail_url?: string;
  created_at: string;
  sentiment: SentimentSummary;
  engagement: EngagementMetrics;
  diagnostics: RetrievalDiagnostics;
  methodology: string;
  comments_sample: CommentItem[];
}

export interface HistorySummary {
  id: string;
  platform: PlatformType;
  url: string;
  target_id: string;
  title?: string;
  author?: string;
  created_at: string;
  total_analyzed: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  extraction_status: string;
}

export interface CompareRequest {
  url_a: string;
  url_b: string;
  sample_limit?: number;
}

export interface ComparisonResult {
  target_a: AnalysisResult;
  target_b: AnalysisResult;
  higher_positive_target?: string;
  higher_dislike_target?: string;
  sentiment_delta_positive: number;
  sentiment_delta_negative: number;
  controversy_delta: number;
  summary_headline: string;
}


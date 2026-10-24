from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PlatformType(str, Enum):
    YOUTUBE = "youtube"
    X = "x"


class SentimentCategory(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CommentItem(BaseModel):
    id: str = Field(..., description="Unique comment or reply identifier")
    author: str = Field(..., description="Username or display name of the commenter")
    text: str = Field(..., description="Raw text of the comment")
    likes: Optional[int] = Field(0, description="Comment like count")
    published_at: Optional[str] = Field(None, description="Published timestamp or relative time")
    sentiment: Optional[SentimentCategory] = Field(None, description="Assigned sentiment category")
    sentiment_score: Optional[float] = Field(None, description="Compound sentiment score (-1.0 to 1.0)")
    sentiment_breakdown: Optional[Dict[str, float]] = Field(None, description="Component scores (pos, neu, neg)")


class SentimentDriverItem(BaseModel):
    keyword: str = Field(..., description="Key theme or phrase extracted from comments")
    count: int = Field(..., description="Number of comments mentioning this theme")
    sentiment: SentimentCategory = Field(..., description="Category: positive or negative driver")
    sample_snippet: Optional[str] = Field(None, description="Representative comment excerpt")


class ScoreBucket(BaseModel):
    label: str = Field(..., description="Bucket label (e.g., Very Negative, Neutral)")
    range_label: str = Field(..., description="Score range representation")
    count: int = Field(0, description="Count of comments falling in bucket")
    percentage: float = Field(0.0, description="Percentage of analyzed comments")


class LikeWeightedMetrics(BaseModel):
    weighted_compound: float = Field(0.0, description="Mean compound score weighted by community likes")
    weighted_positive_pct: float = Field(0.0, description="Community like-weighted positive percentage")
    weighted_neutral_pct: float = Field(0.0, description="Community like-weighted neutral percentage")
    weighted_negative_pct: float = Field(0.0, description="Community like-weighted negative percentage")
    total_weight: int = Field(0, description="Sum of all comment like weights")


class DiagnosticVerdict(BaseModel):
    label: str = Field(..., description="Executive verdict label (e.g. Favorable Reception, Polarized Debate)")
    headline: str = Field(..., description="Detailed analytical diagnostic summary")
    severity: str = Field("info", description="Severity tag: success, info, warning, critical")
    controversy_index: float = Field(0.0, description="Controversy score from 0.0 (consensus) to 100.0 (polarized)")
    controversy_level: str = Field("Low / Consensus", description="Controversy tier classification")


class SentimentSummary(BaseModel):
    positive_count: int = Field(0, description="Number of positive comments")
    neutral_count: int = Field(0, description="Number of neutral comments")
    negative_count: int = Field(0, description="Number of negative comments")
    total_analyzed: int = Field(0, description="Total comments analyzed")
    positive_percentage: float = Field(0.0, description="Percentage positive (0.0 - 100.0)")
    neutral_percentage: float = Field(0.0, description="Percentage neutral (0.0 - 100.0)")
    negative_percentage: float = Field(0.0, description="Percentage negative (0.0 - 100.0)")
    average_compound: float = Field(0.0, description="Mean compound score across analyzed items")
    dislike_drivers: List[SentimentDriverItem] = Field(default_factory=list, description="Top negative themes/reasons")
    praise_drivers: List[SentimentDriverItem] = Field(default_factory=list, description="Top positive themes/reasons")
    score_distribution: List[ScoreBucket] = Field(default_factory=list, description="5-bucket score histogram")
    like_weighted: Optional[LikeWeightedMetrics] = Field(None, description="Sentiment weighted by comment likes")
    verdict: Optional[DiagnosticVerdict] = Field(None, description="Executive diagnostic verdict")


class ThirdPartyDislikes(BaseModel):
    estimated_dislikes: Optional[int] = Field(None, description="Estimated dislike count")
    estimated_likes: Optional[int] = Field(None, description="Third-party recorded like count")
    rating: Optional[float] = Field(None, description="Calculated rating (1 to 5)")
    source: str = Field("Return YouTube Dislike API", description="Data source name")
    is_estimate: bool = Field(True, description="Strictly true: always labeled as estimate")
    limitations_note: str = Field(
        "Third-party statistical estimate based on extension user data; not official YouTube metrics.",
        description="Explicit limitation disclaimer"
    )


class EngagementMetrics(BaseModel):
    views: Optional[int] = Field(None, description="Official view count if available")
    likes: Optional[int] = Field(None, description="Official like count if available")
    comments: Optional[int] = Field(None, description="Reported total comments or replies")
    reposts: Optional[int] = Field(None, description="Platform reposts/retweets count")
    quotes: Optional[int] = Field(None, description="Platform quotes count")
    third_party_dislikes: Optional[ThirdPartyDislikes] = Field(
        None, description="Third-party estimated dislikes (YouTube only)"
    )


class RetrievalDiagnostics(BaseModel):
    reported_comment_count: Optional[int] = Field(None, description="Platform reported count")
    retrieved_records_count: int = Field(0, description="Total raw records pulled from network")
    usable_text_count: int = Field(0, description="Records with non-empty usable text")
    analyzed_count: int = Field(0, description="Count of items successfully processed by sentiment engine")
    extraction_status: str = Field(
        "success",
        description="Status code: 'success', 'partial', 'empty', 'disabled', 'restricted', 'error'"
    )
    failure_reason: Optional[str] = Field(None, description="Detailed failure or error description")
    comments_disabled: bool = Field(False, description="Whether comments are explicitly turned off")
    limitations_note: Optional[str] = Field(None, description="Any public data extraction limitation explanation")


class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="Target video or post URL")
    sample_limit: Optional[int] = Field(100, ge=1, le=500, description="Maximum comments/replies to sample")


class AnalysisResult(BaseModel):
    id: str = Field(..., description="Unique analysis run ID")
    platform: PlatformType = Field(..., description="Target platform")
    url: str = Field(..., description="Normalized URL analyzed")
    target_id: str = Field(..., description="Target video ID or post ID")
    title: Optional[str] = Field(None, description="Video title or post text excerpt")
    author: Optional[str] = Field(None, description="Creator channel or author handle")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL if accessible")
    created_at: str = Field(..., description="ISO 8601 analysis timestamp")
    sentiment: SentimentSummary = Field(..., description="Sentiment analysis aggregate summary")
    engagement: EngagementMetrics = Field(..., description="Platform engagement metrics")
    diagnostics: RetrievalDiagnostics = Field(..., description="Honest retrieval and processing diagnostics")
    methodology: str = Field(..., description="Description of analysis methodology and thresholding")
    comments_sample: List[CommentItem] = Field(default_factory=list, description="Sample of analyzed items")


class HistorySummary(BaseModel):
    id: str
    platform: PlatformType
    url: str
    target_id: str
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: str
    total_analyzed: int
    positive_count: int
    neutral_count: int
    negative_count: int
    extraction_status: str


class CompareRequest(BaseModel):
    url_a: str = Field(..., description="First URL to compare")
    url_b: str = Field(..., description="Second URL to compare")
    sample_limit: Optional[int] = Field(100, ge=1, le=500, description="Max comments/replies to sample per target")


class ComparisonResult(BaseModel):
    target_a: AnalysisResult
    target_b: AnalysisResult
    higher_positive_target: Optional[str] = Field(None, description="Target ID with higher positive sentiment percentage")
    higher_dislike_target: Optional[str] = Field(None, description="Target ID with higher negative sentiment or estimated dislikes")
    sentiment_delta_positive: float = Field(0.0, description="Difference in positive percentage (Target A - Target B)")
    sentiment_delta_negative: float = Field(0.0, description="Difference in negative percentage (Target A - Target B)")
    controversy_delta: float = Field(0.0, description="Difference in controversy index (Target A - Target B)")
    summary_headline: str = Field("", description="Executive comparison summary statement")


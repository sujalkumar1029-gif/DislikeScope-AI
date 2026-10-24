import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import (
    CORS_ORIGINS,
    DEFAULT_SAMPLE_LIMIT,
    MAX_SAMPLE_LIMIT,
)
from backend.database import (
    init_db,
    save_analysis,
    get_analysis,
    list_analyses,
    delete_analysis,
)
from backend.models.schemas import (
    PlatformType,
    AnalyzeRequest,
    AnalysisResult,
    HistorySummary,
    EngagementMetrics,
    CompareRequest,
    ComparisonResult,
)
from backend.services.youtube import (
    extract_youtube_video_id,
    normalize_youtube_url,
    fetch_youtube_metadata,
    fetch_return_youtube_dislike,
    extract_youtube_comments,
)
from backend.services.x_platform import (
    extract_x_post_id,
    normalize_x_url,
    fetch_x_post_data,
)
from backend.services.sentiment import (
    analyze_comments_batch,
    METHODOLOGY_DESCRIPTION,
)
from backend.services.exporter import (
    export_analysis_json,
    export_analysis_csv,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dislikescope")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    logger.info("DislikeScope-AI backend ready.")
    yield


app = FastAPI(
    title="DislikeScope-AI API",
    description="Honest, diagnostic-driven sentiment and dislike analysis for social platforms.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "DislikeScope-AI",
        "version": "1.0.0",
        "platforms_active": ["youtube", "x"],
    }


@app.post("/api/analyze/youtube", response_model=AnalysisResult)
def analyze_youtube(request: AnalyzeRequest):
    """
    Analyzes a YouTube video by URL:
    1. Validates and normalizes video URL
    2. Fetches public metadata and 3rd-party dislike estimates
    3. Retrieves accessible public comments
    4. Runs VADER sentiment analysis
    5. Persists report to SQLite and returns reconciled result
    """
    video_id = extract_youtube_video_id(request.url)
    if not video_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid YouTube URL format. Supported formats include: "
                "https://www.youtube.com/watch?v=VIDEO_ID, https://youtu.be/VIDEO_ID, "
                "https://www.youtube.com/shorts/VIDEO_ID, or raw 11-character video ID."
            ),
        )

    canonical_url = normalize_youtube_url(video_id)
    sample_limit = min(
        max(request.sample_limit or DEFAULT_SAMPLE_LIMIT, 1),
        MAX_SAMPLE_LIMIT,
    )

    # 1. Fetch metadata & estimated dislikes
    title, author, thumbnail_url = fetch_youtube_metadata(video_id)
    dislikes_obj, views, likes = fetch_return_youtube_dislike(video_id)

    # 2. Extract public comments
    raw_comments, diagnostics = extract_youtube_comments(video_id, sample_limit=sample_limit)

    # 3. Analyze sentiment with strict reconciliation
    analyzed_items, sentiment_summary = analyze_comments_batch(raw_comments)

    # 4. Update diagnostics with analyzed count
    diagnostics.analyzed_count = sentiment_summary.total_analyzed
    diagnostics.usable_text_count = len([c for c in raw_comments if c.text and c.text.strip()])

    # Engagement metrics
    engagement = EngagementMetrics(
        views=views,
        likes=likes,
        comments=diagnostics.reported_comment_count,
        third_party_dislikes=dislikes_obj,
    )

    # 5. Assemble final AnalysisResult
    result_id = f"yt_{video_id}_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    result = AnalysisResult(
        id=result_id,
        platform=PlatformType.YOUTUBE,
        url=canonical_url,
        target_id=video_id,
        title=title or f"YouTube Video ({video_id})",
        author=author or "Unknown Creator",
        thumbnail_url=thumbnail_url,
        created_at=created_at,
        sentiment=sentiment_summary,
        engagement=engagement,
        diagnostics=diagnostics,
        methodology=METHODOLOGY_DESCRIPTION,
        comments_sample=analyzed_items,
    )

    # 6. Persist locally to SQLite
    try:
        save_analysis(result)
    except Exception as exc:
        logger.error("Failed to persist analysis %s: %s", result_id, exc)

    return result


@app.post("/api/analyze/x", response_model=AnalysisResult)
def analyze_x(request: AnalyzeRequest):
    """
    Analyzes an X.com / Twitter post:
    1. Validates and normalizes post URL
    2. Fetches public post metadata and engagement metrics
    3. Retrieves accessible public replies (handles login walls honestly)
    4. Runs VADER sentiment analysis on retrieved text
    5. Persists report to SQLite and returns reconciled result
    """
    parsed = extract_x_post_id(request.url)
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid X.com or Twitter URL format. Supported formats include: "
                "https://x.com/username/status/POST_ID or https://twitter.com/username/status/POST_ID."
            ),
        )

    post_id, username = parsed
    canonical_url = normalize_x_url(post_id, username)

    # 1. Fetch public metadata, engagement, diagnostics, and accessible replies
    post_info, engagement, diagnostics, raw_items = fetch_x_post_data(post_id)

    if not post_info and diagnostics.extraction_status == "error":
        raise HTTPException(
            status_code=404 if "not found" in (diagnostics.failure_reason or "").lower() else 502,
            detail=diagnostics.failure_reason or "Failed to retrieve X post.",
        )

    # 2. Analyze sentiment with strict count reconciliation
    analyzed_items, sentiment_summary = analyze_comments_batch(raw_items)

    # 3. Update diagnostics
    diagnostics.analyzed_count = sentiment_summary.total_analyzed
    diagnostics.usable_text_count = len([c for c in raw_items if c.text and c.text.strip()])

    title_text = post_info.get("text", "")[:80] if post_info else f"X Post ({post_id})"
    author_str = f"{post_info.get('author_name', '')} ({post_info.get('author_handle', '')})" if post_info else "Unknown"

    result_id = f"x_{post_id}_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    result = AnalysisResult(
        id=result_id,
        platform=PlatformType.X,
        url=canonical_url,
        target_id=post_id,
        title=title_text or f"X Post ({post_id})",
        author=author_str,
        thumbnail_url=None,
        created_at=created_at,
        sentiment=sentiment_summary,
        engagement=engagement or EngagementMetrics(),
        diagnostics=diagnostics,
        methodology=METHODOLOGY_DESCRIPTION,
        comments_sample=analyzed_items,
    )

    try:
        save_analysis(result)
    except Exception as exc:
        logger.error("Failed to persist analysis %s: %s", result_id, exc)

    return result


@app.get("/api/history", response_model=List[HistorySummary])
def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Returns past analysis runs ordered chronologically (newest first)."""
    return list_analyses(limit=limit, offset=offset)


@app.get("/api/history/{analysis_id}", response_model=AnalysisResult)
def get_history_item(analysis_id: str):
    """Retrieves full analysis report by ID."""
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis report not found.")
    return result


@app.delete("/api/history/{analysis_id}")
def remove_history_item(analysis_id: str):
    """Deletes an analysis report from the local database."""
    deleted = delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis report not found.")
    return {"success": True, "deleted_id": analysis_id}


@app.get("/api/export/{analysis_id}/json")
def export_json(analysis_id: str):
    """Downloads the full analysis report as a JSON file."""
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    json_str = export_analysis_json(result)
    filename = f"dislikescope_{result.platform.value}_{result.target_id}_{analysis_id}.json"

    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/{analysis_id}/csv")
def export_csv(analysis_id: str):
    """Downloads the analysis report and comments breakdown as a CSV file."""
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    csv_str = export_analysis_csv(result)
    filename = f"dislikescope_{result.platform.value}_{result.target_id}_{analysis_id}.csv"

    return Response(
        content=csv_str,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _analyze_target_by_url(url: str, sample_limit: int) -> AnalysisResult:
    """Helper to detect platform and execute analysis for a target URL."""
    clean_url = (url or "").strip()
    if extract_youtube_video_id(clean_url):
        return analyze_youtube(AnalyzeRequest(url=clean_url, sample_limit=sample_limit))
    elif extract_x_post_id(clean_url):
        return analyze_x(AnalyzeRequest(url=clean_url, sample_limit=sample_limit))
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported URL: '{url}'. Please supply a valid YouTube or X.com/Twitter post URL.",
        )


def compute_comparison_result(res_a: AnalysisResult, res_b: AnalysisResult) -> ComparisonResult:
    """Computes comparative deltas, winners, and an executive comparison statement."""
    pos_delta = round(res_a.sentiment.positive_percentage - res_b.sentiment.positive_percentage, 1)
    neg_delta = round(res_a.sentiment.negative_percentage - res_b.sentiment.negative_percentage, 1)

    ci_a = res_a.sentiment.verdict.controversy_index if res_a.sentiment.verdict else 0.0
    ci_b = res_b.sentiment.verdict.controversy_index if res_b.sentiment.verdict else 0.0
    controversy_delta = round(ci_a - ci_b, 1)

    # Higher positive target
    if res_a.sentiment.positive_percentage > res_b.sentiment.positive_percentage:
        higher_pos = res_a.target_id
    elif res_b.sentiment.positive_percentage > res_a.sentiment.positive_percentage:
        higher_pos = res_b.target_id
    else:
        higher_pos = None

    # Higher negative target
    if res_a.sentiment.negative_percentage > res_b.sentiment.negative_percentage:
        higher_neg = res_a.target_id
    elif res_b.sentiment.negative_percentage > res_a.sentiment.negative_percentage:
        higher_neg = res_b.target_id
    else:
        higher_neg = None

    title_a = res_a.title or res_a.target_id
    title_b = res_b.title or res_b.target_id

    if higher_pos == res_a.target_id and higher_neg == res_b.target_id:
        headline = f"'{title_a}' demonstrates superior positive sentiment (+{pos_delta}%) with lower negative backlash compared to '{title_b}'."
    elif higher_pos == res_b.target_id and higher_neg == res_a.target_id:
        headline = f"'{title_b}' demonstrates superior positive sentiment (+{abs(pos_delta)}%) with lower negative backlash compared to '{title_a}'."
    elif pos_delta == 0 and neg_delta == 0:
        headline = "Both targets exhibit virtually equivalent audience sentiment and reaction ratios."
    else:
        headline = f"Comparison shows a {abs(pos_delta)}% positive differential and a {abs(neg_delta)}% negative differential between targets."

    return ComparisonResult(
        target_a=res_a,
        target_b=res_b,
        higher_positive_target=higher_pos,
        higher_dislike_target=higher_neg,
        sentiment_delta_positive=pos_delta,
        sentiment_delta_negative=neg_delta,
        controversy_delta=controversy_delta,
        summary_headline=headline,
    )


@app.post("/api/compare", response_model=ComparisonResult)
def compare_urls(request: CompareRequest):
    """
    Compares two social targets head-to-head by URL:
    1. Analyzes both targets independently
    2. Calculates side-by-side metric deltas and controversy comparison
    3. Produces an executive benchmark result
    """
    sample_limit = min(
        max(request.sample_limit or DEFAULT_SAMPLE_LIMIT, 1),
        MAX_SAMPLE_LIMIT,
    )

    res_a = _analyze_target_by_url(request.url_a, sample_limit)
    res_b = _analyze_target_by_url(request.url_b, sample_limit)

    return compute_comparison_result(res_a, res_b)


@app.get("/api/compare", response_model=ComparisonResult)
def compare_history_items(
    id_a: str = Query(..., description="First analysis report ID"),
    id_b: str = Query(..., description="Second analysis report ID"),
):
    """Compares two existing historical analysis reports from SQLite."""
    res_a = get_analysis(id_a)
    if not res_a:
        raise HTTPException(status_code=404, detail=f"Analysis report '{id_a}' not found.")

    res_b = get_analysis(id_b)
    if not res_b:
        raise HTTPException(status_code=404, detail=f"Analysis report '{id_b}' not found.")

    return compute_comparison_result(res_a, res_b)


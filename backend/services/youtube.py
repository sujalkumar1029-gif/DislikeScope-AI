import re
import logging
from typing import Optional, Tuple, List
from itertools import islice
import requests
from youtube_comment_downloader import YoutubeCommentDownloader
from backend.models.schemas import (
    CommentItem,
    ThirdPartyDislikes,
    EngagementMetrics,
    RetrievalDiagnostics,
)
from backend.config import REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

# Standard YouTube 11-character alphanumeric/dash/underscore ID
YOUTUBE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")

# URL extraction patterns with strict boundaries
YOUTUBE_URL_PATTERNS = [
    # standard watch?v=...
    re.compile(r"(?:https?://)?(?:www\.|m\.)?youtube\.com/watch\?(?:[^#]*&)?v=([a-zA-Z0-9_-]{11})(?![a-zA-Z0-9_-])"),
    # youtu.be/...
    re.compile(r"(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})(?![a-zA-Z0-9_-])"),
    # embed/...
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?![a-zA-Z0-9_-])"),
    # shorts/...
    re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})(?![a-zA-Z0-9_-])"),
    # raw 11 character ID
    re.compile(r"^([a-zA-Z0-9_-]{11})$"),
]


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    Extracts and validates the 11-character YouTube video ID from various supported URL formats.
    Returns the normalized ID or None if the URL is invalid or malformed.
    """
    if not url:
        return None

    clean_url = url.strip()
    for pattern in YOUTUBE_URL_PATTERNS:
        match = pattern.search(clean_url)
        if match:
            vid = match.group(1)
            if YOUTUBE_ID_PATTERN.match(vid):
                return vid
    return None


def normalize_youtube_url(video_id: str) -> str:
    """Returns the canonical watch URL for a video ID."""
    return f"https://www.youtube.com/watch?v={video_id}"


def fetch_youtube_metadata(video_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Fetches public title, author, and thumbnail via YouTube oEmbed service.
    Returns (title, author, thumbnail_url).
    """
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    title = None
    author = None
    thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    try:
        resp = requests.get(
            oembed_url,
            headers={"User-Agent": "DislikeScope-AI/1.0"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            title = data.get("title")
            author = data.get("author_name")
            thumbnail_url = data.get("thumbnail_url", thumbnail_url)
    except Exception as exc:
        logger.warning("Could not fetch oEmbed metadata for %s: %s", video_id, exc)

    return title, author, thumbnail_url


def fetch_return_youtube_dislike(video_id: str) -> Tuple[Optional[ThirdPartyDislikes], Optional[int], Optional[int]]:
    """
    Fetches engagement and third-party estimated dislikes from Return YouTube Dislike API.
    Returns (ThirdPartyDislikes, views, likes).
    Always clearly marked as a third-party estimate.
    """
    ryd_url = f"https://returnyoutubedislikeapi.com/votes?videoId={video_id}"
    dislikes_obj = None
    views = None
    likes = None

    try:
        resp = requests.get(
            ryd_url,
            headers={"User-Agent": "DislikeScope-AI/1.0"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            views = data.get("viewCount")
            likes = data.get("likes")
            dislikes_count = data.get("dislikes")
            rating = data.get("rating")

            dislikes_obj = ThirdPartyDislikes(
                estimated_dislikes=dislikes_count,
                estimated_likes=likes,
                rating=round(rating, 2) if rating is not None else None,
                source="Return YouTube Dislike API",
                is_estimate=True,
                limitations_note=(
                    "Third-party statistical estimate extrapolated from extension users and historical archives; "
                    "not official YouTube metrics."
                ),
            )
    except Exception as exc:
        logger.warning("Return YouTube Dislike API error for %s: %s", video_id, exc)

    return dislikes_obj, views, likes


def extract_youtube_comments(
    video_id: str,
    sample_limit: int = 100,
) -> Tuple[List[CommentItem], RetrievalDiagnostics]:
    """
    Extracts accessible public comments using YoutubeCommentDownloader.
    Returns (raw_comment_items, diagnostics).
    """
    downloader = YoutubeCommentDownloader()
    canonical_url = normalize_youtube_url(video_id)
    raw_items: List[CommentItem] = []
    failure_reason: Optional[str] = None
    comments_disabled = False
    status = "success"

    try:
        generator = downloader.get_comments_from_url(canonical_url)
        # Limit extraction to sample_limit
        for raw in islice(generator, sample_limit):
            cid = str(raw.get("cid") or f"yt-{len(raw_items) + 1}")
            author = str(raw.get("author") or "Anonymous")
            text = str(raw.get("text") or "")
            votes = raw.get("votes", 0)
            try:
                votes_int = int(votes) if votes else 0
            except (ValueError, TypeError):
                votes_int = 0
            pub_time = str(raw.get("time") or "")

            raw_items.append(
                CommentItem(
                    id=cid,
                    author=author,
                    text=text,
                    likes=votes_int,
                    published_at=pub_time or None,
                )
            )

        retrieved_count = len(raw_items)
        usable_text_count = sum(1 for c in raw_items if c.text and c.text.strip())

        if retrieved_count == 0:
            status = "empty"
            failure_reason = "No accessible public comments were found for this video. Comments may be turned off, none have been posted, or anonymous access is restricted."
        else:
            status = "success"

    except Exception as exc:
        logger.error("Error retrieving YouTube comments for %s: %s", video_id, exc)
        err_msg = str(exc).lower()
        if "disabled" in err_msg or "turned off" in err_msg:
            comments_disabled = True
            status = "disabled"
            failure_reason = "Comments are explicitly turned off/disabled for this video."
        else:
            status = "error"
            failure_reason = f"Extraction failed: {str(exc)}"

        retrieved_count = 0
        usable_text_count = 0

    diagnostics = RetrievalDiagnostics(
        reported_comment_count=None,
        retrieved_records_count=retrieved_count,
        usable_text_count=usable_text_count,
        analyzed_count=0, # populated after sentiment analysis
        extraction_status=status,
        failure_reason=failure_reason,
        comments_disabled=comments_disabled,
        limitations_note=(
            "Comment retrieval relies on publicly accessible web pages without authentication. "
            "Private videos, geo-blocked content, or active CAPTCHAs may restrict retrieval."
        ),
    )

    return raw_items, diagnostics

import re
import logging
from typing import Optional, Tuple, List
import requests
from backend.models.schemas import (
    CommentItem,
    EngagementMetrics,
    RetrievalDiagnostics,
)
from backend.config import REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

# Supported X / Twitter URL patterns
X_URL_PATTERNS = [
    # standard x.com/user/status/123...
    re.compile(r"(?:https?://)?(?:www\.|mobile\.)?(?:twitter\.com|x\.com)/(?:#!/)?([a-zA-Z0-9_]+)/status(?:es)?/(\d+)"),
    # raw numeric tweet ID
    re.compile(r"^(\d{1,25})$"),
]


def extract_x_post_id(url: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    Extracts tweet/post ID and optional username from X.com or Twitter.com URLs.
    Returns (post_id, username) or None if invalid.
    """
    if not url:
        return None

    clean_url = url.strip()
    for pattern in X_URL_PATTERNS:
        match = pattern.search(clean_url)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                username = groups[0]
                post_id = groups[1]
                return post_id, username
            elif len(groups) == 1:
                return groups[0], None
    return None


def normalize_x_url(post_id: str, username: Optional[str] = None) -> str:
    """Returns canonical x.com post URL."""
    handle = username if username and username.lower() not in ("i", "status") else "i"
    return f"https://x.com/{handle}/status/{post_id}"


def fetch_x_post_data(
    post_id: str,
) -> Tuple[Optional[dict], Optional[EngagementMetrics], RetrievalDiagnostics, List[CommentItem]]:
    """
    Retrieves public post metadata and replies (if accessible) via Twitter syndication API.
    Handles login walls and access boundaries honestly without fabricating sentiment.
    """
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={post_id}&token=5"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Accept": "application/json",
    }

    raw_items: List[CommentItem] = []
    reported_replies: Optional[int] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    reposts: Optional[int] = None
    post_info = None

    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        if resp.status_code == 404:
            diagnostics = RetrievalDiagnostics(
                reported_comment_count=None,
                retrieved_records_count=0,
                usable_text_count=0,
                analyzed_count=0,
                extraction_status="error",
                failure_reason="X post not found or removed.",
                limitations_note="Post may have been deleted, suspended, or made private.",
            )
            return None, None, diagnostics, []

        if resp.status_code != 200:
            diagnostics = RetrievalDiagnostics(
                reported_comment_count=None,
                retrieved_records_count=0,
                usable_text_count=0,
                analyzed_count=0,
                extraction_status="error",
                failure_reason=f"X syndication endpoint returned status HTTP {resp.status_code}.",
                limitations_note="Platform rate limits or access controls prevented data retrieval.",
            )
            return None, None, diagnostics, []

        data = resp.json()
        post_info = {
            "id": data.get("id_str") or post_id,
            "text": data.get("text", ""),
            "author_name": data.get("user", {}).get("name", "Unknown"),
            "author_handle": "@" + data.get("user", {}).get("screen_name", "unknown"),
            "created_at": data.get("created_at"),
        }

        likes = data.get("favorite_count")
        reported_replies = data.get("conversation_count")
        reposts = data.get("retweet_count")

        # Check if parent or thread context includes replies
        parent = data.get("parent")
        if parent and isinstance(parent, dict):
            parent_text = parent.get("text", "").strip()
            if parent_text:
                raw_items.append(
                    CommentItem(
                        id=parent.get("id_str") or "parent_tweet",
                        author=parent.get("user", {}).get("name", "Parent Author"),
                        text=parent_text,
                        likes=parent.get("favorite_count", 0),
                        published_at=parent.get("created_at"),
                    )
                )

        retrieved_count = len(raw_items)
        usable_count = sum(1 for c in raw_items if c.text and c.text.strip())

        if retrieved_count == 0:
            # Crucial: X blocks public anonymous scraping of thread replies behind login walls.
            # We explicitly report this restriction.
            extraction_status = "restricted"
            failure_reason = (
                "X.com restricts public anonymous retrieval of thread replies behind authentication login walls. "
                "Per the DislikeScope-AI Truth Policy, reply sentiment is not fabricated. "
                "Engagement metrics and post metadata were successfully retrieved."
            )
        else:
            extraction_status = "partial"
            failure_reason = "Partial thread context retrieved. Full reply tree is restricted by platform login wall."

        diagnostics = RetrievalDiagnostics(
            reported_comment_count=reported_replies,
            retrieved_records_count=retrieved_count,
            usable_text_count=usable_count,
            analyzed_count=0, # Populated after sentiment analysis
            extraction_status=extraction_status,
            failure_reason=failure_reason,
            comments_disabled=False,
            limitations_note=(
                "X.com (Twitter) requires user authentication to browse full reply threads. "
                "DislikeScope-AI strictly enforces genuine data collection without bypassing platform boundaries."
            ),
        )

        engagement = EngagementMetrics(
            views=views,
            likes=likes,
            comments=reported_replies,
            reposts=reposts,
            third_party_dislikes=None, # Dislikes API only applies to YouTube
        )

        return post_info, engagement, diagnostics, raw_items

    except Exception as exc:
        logger.error("Error retrieving X post %s: %s", post_id, exc)
        diagnostics = RetrievalDiagnostics(
            reported_comment_count=None,
            retrieved_records_count=0,
            usable_text_count=0,
            analyzed_count=0,
            extraction_status="error",
            failure_reason=f"Failed to connect to X syndication service: {str(exc)}",
            limitations_note="Network connection failure or endpoint timeout.",
        )
        return None, None, diagnostics, []

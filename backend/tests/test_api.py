from unittest.mock import patch
from backend.models.schemas import CommentItem, RetrievalDiagnostics


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "youtube" in data["platforms_active"]


def test_analyze_youtube_invalid_url(client):
    response = client.post("/api/analyze/youtube", json={"url": "not_a_valid_youtube_url"})
    assert response.status_code == 400
    assert "Invalid YouTube URL format" in response.json()["detail"]


@patch("backend.main.fetch_youtube_metadata")
@patch("backend.main.fetch_return_youtube_dislike")
@patch("backend.main.extract_youtube_comments")
def test_analyze_youtube_success(mock_extract, mock_dislike, mock_meta, client):
    mock_meta.return_value = ("Sample Video Title", "Sample Creator", "https://example.com/thumb.jpg")
    mock_dislike.return_value = (None, 5000, 200)
    mock_extract.return_value = (
        [
            CommentItem(id="c1", author="Alice", text="Loved this video, amazing explanation!"),
            CommentItem(id="c2", author="Bob", text="Terrible video, completely hated it."),
        ],
        RetrievalDiagnostics(
            retrieved_records_count=2,
            usable_text_count=2,
            analyzed_count=2,
            extraction_status="success",
        ),
    )

    response = client.post(
        "/api/analyze/youtube",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "sample_limit": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "youtube"
    assert data["target_id"] == "dQw4w9WgXcQ"
    assert data["sentiment"]["total_analyzed"] == 2
    assert data["sentiment"]["positive_count"] == 1
    assert data["sentiment"]["negative_count"] == 1
    assert data["diagnostics"]["analyzed_count"] == 2

    # Check that it appears in history
    hist_response = client.get("/api/history")
    assert hist_response.status_code == 200
    assert len(hist_response.json()) >= 1
    assert hist_response.json()[0]["id"] == data["id"]


def test_analyze_x_invalid_url(client):
    response = client.post("/api/analyze/x", json={"url": "https://not_x.com/invalid"})
    assert response.status_code == 400
    assert "Invalid X.com or Twitter URL" in response.json()["detail"]


@patch("backend.main.fetch_x_post_data")
def test_analyze_x_success(mock_fetch_x, client):
    from backend.models.schemas import EngagementMetrics
    mock_fetch_x.return_value = (
        {
            "id": "20",
            "text": "just setting up my twttr",
            "author_name": "Jack",
            "author_handle": "@jack",
            "created_at": "2006-03-21T20:50:14.000Z",
        },
        EngagementMetrics(likes=310000, comments=18000, reposts=120000),
        RetrievalDiagnostics(
            reported_comment_count=18000,
            retrieved_records_count=0,
            usable_text_count=0,
            analyzed_count=0,
            extraction_status="restricted",
            failure_reason="X.com restricts public anonymous retrieval of thread replies behind authentication login walls.",
        ),
        [], # 0 replies due to login wall
    )

    response = client.post("/api/analyze/x", json={"url": "https://x.com/jack/status/20"})
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "x"
    assert data["target_id"] == "20"
    assert data["engagement"]["likes"] == 310000
    assert data["engagement"]["comments"] == 18000
    # Strict truth verification: 0 replies retrieved -> 0 analyzed -> no fabricated sentiment
    assert data["sentiment"]["total_analyzed"] == 0
    assert data["sentiment"]["positive_count"] == 0
    assert data["sentiment"]["negative_count"] == 0
    assert data["diagnostics"]["extraction_status"] == "restricted"
    assert data["diagnostics"]["analyzed_count"] == 0


def test_compare_history_items(client):
    from backend.database import save_analysis
    from backend.models.schemas import (
        AnalysisResult,
        PlatformType,
        SentimentSummary,
        EngagementMetrics,
        RetrievalDiagnostics,
        DiagnosticVerdict,
    )

    item_a = AnalysisResult(
        id="test_a_123",
        platform=PlatformType.YOUTUBE,
        url="https://www.youtube.com/watch?v=aaaaaaaaaaa",
        target_id="aaaaaaaaaaa",
        title="Video A - Loved",
        created_at="2026-10-24T00:00:00Z",
        sentiment=SentimentSummary(
            positive_count=80,
            neutral_count=10,
            negative_count=10,
            total_analyzed=100,
            positive_percentage=80.0,
            neutral_percentage=10.0,
            negative_percentage=10.0,
            average_compound=0.6,
            verdict=DiagnosticVerdict(
                label="Overwhelming Audience Praise",
                headline="High praise",
                severity="success",
                controversy_index=20.0,
                controversy_level="Low / Consensus",
            ),
        ),
        engagement=EngagementMetrics(views=10000, likes=1500),
        diagnostics=RetrievalDiagnostics(retrieved_records_count=100, usable_text_count=100, analyzed_count=100),
        methodology="VADER",
        comments_sample=[],
    )

    item_b = AnalysisResult(
        id="test_b_456",
        platform=PlatformType.YOUTUBE,
        url="https://www.youtube.com/watch?v=bbbbbbbbbbb",
        target_id="bbbbbbbbbbb",
        title="Video B - Disliked",
        created_at="2026-10-24T00:00:00Z",
        sentiment=SentimentSummary(
            positive_count=20,
            neutral_count=20,
            negative_count=60,
            total_analyzed=100,
            positive_percentage=20.0,
            neutral_percentage=20.0,
            negative_percentage=60.0,
            average_compound=-0.4,
            verdict=DiagnosticVerdict(
                label="Severe Audience Backlash",
                headline="Heavy backlash",
                severity="critical",
                controversy_index=45.0,
                controversy_level="Moderate",
            ),
        ),
        engagement=EngagementMetrics(views=8000, likes=200),
        diagnostics=RetrievalDiagnostics(retrieved_records_count=100, usable_text_count=100, analyzed_count=100),
        methodology="VADER",
        comments_sample=[],
    )

    save_analysis(item_a)
    save_analysis(item_b)

    resp = client.get("/api/compare?id_a=test_a_123&id_b=test_b_456")
    assert resp.status_code == 200
    comp = resp.json()

    assert comp["higher_positive_target"] == "aaaaaaaaaaa"
    assert comp["higher_dislike_target"] == "bbbbbbbbbbb"
    assert comp["sentiment_delta_positive"] == 60.0 # 80 - 20
    assert comp["sentiment_delta_negative"] == -50.0 # 10 - 60
    assert "Video A - Loved" in comp["summary_headline"]


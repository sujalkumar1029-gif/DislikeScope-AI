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

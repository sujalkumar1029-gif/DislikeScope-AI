import json
from backend.models.schemas import (
    AnalysisResult,
    PlatformType,
    SentimentSummary,
    EngagementMetrics,
    RetrievalDiagnostics,
    CommentItem,
    SentimentCategory,
)
from backend.database import save_analysis
from backend.services.exporter import export_analysis_json, export_analysis_csv


def make_sample_result():
    return AnalysisResult(
        id="yt_export_test",
        platform=PlatformType.YOUTUBE,
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        target_id="dQw4w9WgXcQ",
        title="Rick Astley - Never Gonna Give You Up",
        author="Rick Astley",
        thumbnail_url="https://example.com/thumb.jpg",
        created_at="2026-10-17T11:00:00Z",
        sentiment=SentimentSummary(
            positive_count=2,
            neutral_count=1,
            negative_count=0,
            total_analyzed=3,
            positive_percentage=66.7,
            neutral_percentage=33.3,
            negative_percentage=0.0,
            average_compound=0.45,
        ),
        engagement=EngagementMetrics(views=1000000, likes=50000),
        diagnostics=RetrievalDiagnostics(
            reported_comment_count=1000,
            retrieved_records_count=3,
            usable_text_count=3,
            analyzed_count=3,
            extraction_status="success",
        ),
        methodology="VADER Lexicon Model",
        comments_sample=[
            CommentItem(
                id="c1",
                author="Fan1",
                text="Legendary song!",
                likes=10,
                sentiment=SentimentCategory.POSITIVE,
                sentiment_score=0.8,
            )
        ],
    )


def test_export_json():
    result = make_sample_result()
    json_str = export_analysis_json(result)
    data = json.loads(json_str)
    assert data["id"] == "yt_export_test"
    assert data["sentiment"]["total_analyzed"] == 3
    assert len(data["comments_sample"]) == 1


def test_export_csv():
    result = make_sample_result()
    csv_str = export_analysis_csv(result)
    assert "# DISLIKESCOPE-AI ANALYSIS REPORT" in csv_str
    assert "yt_export_test" in csv_str
    assert "# RETRIEVAL DIAGNOSTICS" in csv_str
    assert "# SENTIMENT SUMMARY" in csv_str
    assert "# ANALYZED COMMENTS SAMPLE" in csv_str
    assert "Legendary song!" in csv_str


def test_export_endpoints(client):
    result = make_sample_result()
    save_analysis(result)

    # Test JSON export endpoint
    resp_json = client.get("/api/export/yt_export_test/json")
    assert resp_json.status_code == 200
    assert resp_json.headers["content-type"] == "application/json"
    assert "attachment" in resp_json.headers["content-disposition"]
    data = resp_json.json()
    assert data["id"] == "yt_export_test"

    # Test CSV export endpoint
    resp_csv = client.get("/api/export/yt_export_test/csv")
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.headers["content-type"]
    assert "attachment" in resp_csv.headers["content-disposition"]
    assert "DISLIKESCOPE-AI ANALYSIS REPORT" in resp_csv.text

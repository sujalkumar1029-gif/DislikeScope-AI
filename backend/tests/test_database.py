from backend.models.schemas import (
    AnalysisResult,
    PlatformType,
    SentimentSummary,
    EngagementMetrics,
    RetrievalDiagnostics,
    CommentItem,
    SentimentCategory,
)
from backend.database import save_analysis, get_analysis, list_analyses, delete_analysis


def test_database_crud():
    sample_result = AnalysisResult(
        id="yt_test123_abc",
        platform=PlatformType.YOUTUBE,
        url="https://www.youtube.com/watch?v=test1234567",
        target_id="test1234567",
        title="Test YouTube Video",
        author="Test Creator",
        thumbnail_url="https://example.com/thumb.jpg",
        created_at="2026-10-17T11:00:00Z",
        sentiment=SentimentSummary(
            positive_count=10,
            neutral_count=5,
            negative_count=5,
            total_analyzed=20,
            positive_percentage=50.0,
            neutral_percentage=25.0,
            negative_percentage=25.0,
            average_compound=0.25,
        ),
        engagement=EngagementMetrics(views=1000, likes=100),
        diagnostics=RetrievalDiagnostics(
            reported_comment_count=20,
            retrieved_records_count=20,
            usable_text_count=20,
            analyzed_count=20,
            extraction_status="success",
        ),
        methodology="VADER Lexicon Model",
        comments_sample=[
            CommentItem(
                id="c1",
                author="User1",
                text="Great video!",
                likes=5,
                sentiment=SentimentCategory.POSITIVE,
                sentiment_score=0.6,
            )
        ],
    )

    # 1. Save
    save_analysis(sample_result)

    # 2. Get by ID
    retrieved = get_analysis("yt_test123_abc")
    assert retrieved is not None
    assert retrieved.id == "yt_test123_abc"
    assert retrieved.target_id == "test1234567"
    assert retrieved.sentiment.total_analyzed == 20
    assert len(retrieved.comments_sample) == 1
    assert retrieved.comments_sample[0].sentiment == SentimentCategory.POSITIVE

    # 3. List
    history = list_analyses()
    assert len(history) >= 1
    assert any(h.id == "yt_test123_abc" for h in history)

    # 4. Delete
    deleted = delete_analysis("yt_test123_abc")
    assert deleted is True
    assert get_analysis("yt_test123_abc") is None

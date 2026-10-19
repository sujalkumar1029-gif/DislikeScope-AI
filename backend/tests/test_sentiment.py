from backend.models.schemas import CommentItem, SentimentCategory
from backend.services.sentiment import analyze_text_sentiment, analyze_comments_batch


def test_analyze_text_sentiment_categories():
    pos_cat, pos_compound, _ = analyze_text_sentiment("This is wonderful, brilliant, and I absolutely love it! ❤️")
    assert pos_cat == SentimentCategory.POSITIVE
    assert pos_compound >= 0.05

    neg_cat, neg_compound, _ = analyze_text_sentiment("This is terrible, disgusting, and completely unwatchable garbage.")
    assert neg_cat == SentimentCategory.NEGATIVE
    assert neg_compound <= -0.05

    neu_cat, neu_compound, _ = analyze_text_sentiment("The video length is 12 minutes and 30 seconds.")
    assert neu_cat == SentimentCategory.NEUTRAL
    assert -0.05 < neu_compound < 0.05


def test_analyze_comments_batch_reconciliation():
    raw_comments = [
        CommentItem(id="1", author="UserA", text="Outstanding work, really enjoyed this!"),
        CommentItem(id="2", author="UserB", text="Awful, hate this so much."),
        CommentItem(id="3", author="UserC", text="Here is a neutral statement about the facts."),
        CommentItem(id="4", author="UserD", text=""), # empty text - must be filtered
        CommentItem(id="5", author="UserE", text="   "), # whitespace - must be filtered
    ]

    analyzed, summary = analyze_comments_batch(raw_comments)

    # Only 3 valid comments
    assert len(analyzed) == 3
    assert summary.total_analyzed == 3
    assert summary.positive_count + summary.neutral_count + summary.negative_count == summary.total_analyzed
    assert summary.positive_count == 1
    assert summary.negative_count == 1
    assert summary.neutral_count == 1

    # Check percentages
    total_pct = summary.positive_percentage + summary.neutral_percentage + summary.negative_percentage
    assert abs(total_pct - 100.0) < 0.2


def test_analyze_comments_batch_empty():
    analyzed, summary = analyze_comments_batch([])
    assert len(analyzed) == 0
    assert summary.total_analyzed == 0
    assert summary.positive_count == 0
    assert summary.neutral_count == 0
    assert summary.negative_count == 0
    assert summary.positive_percentage == 0.0
    assert summary.neutral_percentage == 0.0
    assert summary.negative_percentage == 0.0
    assert summary.average_compound == 0.0

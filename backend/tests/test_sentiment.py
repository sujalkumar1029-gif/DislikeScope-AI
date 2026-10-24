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
    assert summary.dislike_drivers == []
    assert summary.praise_drivers == []
    assert summary.verdict is not None
    assert summary.verdict.label == "Zero Comments Available"


def test_sentiment_drivers_and_distribution():
    raw_comments = [
        CommentItem(id="1", author="UserA", text="The sound design and audio mixing is absolute perfection, stunning soundtrack!"),
        CommentItem(id="2", author="UserB", text="Brilliant explanation, love the clean soundtrack and editing."),
        CommentItem(id="3", author="UserC", text="Horrible clickbait title, totally misleading and scam."),
        CommentItem(id="4", author="UserD", text="I hate this terrible clickbait title, waste of time!"),
        CommentItem(id="5", author="UserE", text="Normal commentary on general topic."),
    ]

    _, summary = analyze_comments_batch(raw_comments)

    assert summary.total_analyzed == 5
    assert len(summary.score_distribution) == 5
    # Distribution sum equals total
    assert sum(b.count for b in summary.score_distribution) == 5

    # Check praise driver extraction
    praise_keywords = [d.keyword for d in summary.praise_drivers]
    assert any("soundtrack" in kw or "audio" in kw or "explanation" in kw for kw in praise_keywords)

    # Check dislike driver extraction
    dislike_keywords = [d.keyword for d in summary.dislike_drivers]
    assert any("clickbait" in kw or "misleading" in kw or "scam" in kw for kw in dislike_keywords)


def test_like_weighted_metrics_amplification():
    raw_comments = [
        # Vocal minority: 2 negative comments with 0 likes
        CommentItem(id="1", author="UserA", text="This is awful and boring.", likes=0),
        CommentItem(id="2", author="UserB", text="Terrible video.", likes=0),
        # Silent majority: 1 positive comment with 1000 likes
        CommentItem(id="3", author="UserC", text="Amazing masterpiece, loved every second!", likes=1000),
    ]

    _, summary = analyze_comments_batch(raw_comments)

    # Raw counts: 66.7% negative, 33.3% positive
    assert summary.negative_count == 2
    assert summary.positive_count == 1
    assert summary.negative_percentage > summary.positive_percentage

    # Like-weighted: positive should overwhelmingly dominate because of 1000 likes
    assert summary.like_weighted is not None
    assert summary.like_weighted.weighted_positive_pct > 90.0
    assert summary.like_weighted.weighted_compound > 0.5


def test_controversy_index_and_verdict_polarization():
    # Equal split of strong positive and strong negative comments
    raw_comments = [
        CommentItem(id="1", author="User1", text="Best thing ever made, phenomenal!"),
        CommentItem(id="2", author="User2", text="Incredible masterpiece, 10/10!"),
        CommentItem(id="3", author="User3", text="Disgusting garbage, hate everything about this!"),
        CommentItem(id="4", author="User4", text="Worst video on the platform, totally horrific!"),
    ]

    _, summary = analyze_comments_batch(raw_comments)

    assert summary.verdict is not None
    # High controversy due to even split of passionate extremes
    assert summary.verdict.controversy_index >= 50.0
    assert summary.verdict.label == "Polarized Community Debate"


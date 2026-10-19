import logging
from typing import List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from backend.models.schemas import (
    CommentItem,
    SentimentCategory,
    SentimentSummary,
)

logger = logging.getLogger(__name__)

# Initialize analyzer singleton
_analyzer = SentimentIntensityAnalyzer()

METHODOLOGY_DESCRIPTION = (
    "VADER (Valence Aware Dictionary and sEntiment Reasoner) Lexicon and Rule-Based Model "
    "specifically tuned for social media text and micro-syntax (emojis, punctuation, capitalization, slang). "
    "Thresholds: Positive (compound >= +0.05), Neutral (-0.05 < compound < +0.05), Negative (compound <= -0.05)."
)


def analyze_text_sentiment(text: str) -> Tuple[SentimentCategory, float, dict]:
    """
    Analyzes a single text string using VADER.
    Returns (category, compound_score, breakdown_dict).
    """
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    breakdown = {
        "pos": scores["pos"],
        "neu": scores["neu"],
        "neg": scores["neg"],
    }

    if compound >= 0.05:
        category = SentimentCategory.POSITIVE
    elif compound <= -0.05:
        category = SentimentCategory.NEGATIVE
    else:
        category = SentimentCategory.NEUTRAL

    return category, compound, breakdown


def analyze_comments_batch(
    raw_comments: List[CommentItem],
) -> Tuple[List[CommentItem], SentimentSummary]:
    """
    Processes a list of CommentItems, filtering out items without usable text,
    assigning sentiment classification, and producing a reconciled SentimentSummary.
    """
    analyzed_items: List[CommentItem] = []
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    compound_sum = 0.0

    for item in raw_comments:
        text = (item.text or "").strip()
        if not text:
            # Skip empty or whitespace-only records
            continue

        cat, compound, breakdown = analyze_text_sentiment(text)
        item.sentiment = cat
        item.sentiment_score = round(compound, 4)
        item.sentiment_breakdown = breakdown

        if cat == SentimentCategory.POSITIVE:
            positive_count += 1
        elif cat == SentimentCategory.NEGATIVE:
            negative_count += 1
        else:
            neutral_count += 1

        compound_sum += compound
        analyzed_items.append(item)

    total = len(analyzed_items)
    if total > 0:
        pos_pct = round((positive_count / total) * 100.0, 1)
        neu_pct = round((neutral_count / total) * 100.0, 1)
        neg_pct = round((negative_count / total) * 100.0, 1)
        avg_comp = round(compound_sum / total, 4)
    else:
        pos_pct = 0.0
        neu_pct = 0.0
        neg_pct = 0.0
        avg_comp = 0.0

    summary = SentimentSummary(
        positive_count=positive_count,
        neutral_count=neutral_count,
        negative_count=negative_count,
        total_analyzed=total,
        positive_percentage=pos_pct,
        neutral_percentage=neu_pct,
        negative_percentage=neg_pct,
        average_compound=avg_comp,
    )

    return analyzed_items, summary

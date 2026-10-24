import re
import math
import logging
from collections import Counter
from typing import List, Tuple, Dict, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from backend.models.schemas import (
    CommentItem,
    SentimentCategory,
    SentimentSummary,
    SentimentDriverItem,
    ScoreBucket,
    LikeWeightedMetrics,
    DiagnosticVerdict,
)

logger = logging.getLogger(__name__)

# Initialize analyzer singleton
_analyzer = SentimentIntensityAnalyzer()

METHODOLOGY_DESCRIPTION = (
    "VADER (Valence Aware Dictionary and sEntiment Reasoner) Lexicon and Rule-Based Model "
    "specifically tuned for social media text and micro-syntax (emojis, punctuation, capitalization, slang). "
    "Thresholds: Positive (compound >= +0.05), Neutral (-0.05 < compound < +0.05), Negative (compound <= -0.05)."
)

# Common English stopwords + platform noise terms
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "arent", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "cant", "cannot", "could", "couldnt", "did", "didnt", "do", "does", "doesnt",
    "doing", "dont", "down", "during", "each", "few", "for", "from", "further", "had", "hadnt",
    "has", "hasnt", "have", "havent", "having", "he", "hed", "hell", "hes", "her", "here",
    "heres", "hers", "herself", "him", "himself", "his", "how", "hows", "i", "id", "ill", "im",
    "ive", "if", "in", "into", "is", "isnt", "it", "its", "itself", "lets", "me", "more", "most",
    "mustnt", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shant", "she",
    "shed", "shell", "shes", "should", "shouldnt", "so", "some", "such", "than", "that", "thats",
    "the", "their", "theirs", "them", "themselves", "then", "there", "theres", "these", "they",
    "theyd", "theyll", "theyre", "theyve", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasnt", "we", "wed", "well", "were", "weve", "werent",
    "what", "whats", "when", "whens", "where", "wheres", "which", "while", "who", "whos",
    "whom", "why", "whys", "with", "wont", "would", "wouldnt", "you", "youd", "youll", "youre",
    "youve", "your", "yours", "yourself", "yourselves",
    # Platform / conversational filler
    "video", "videos", "youtube", "twitter", "channel", "watch", "watching", "watched",
    "like", "likes", "comment", "comments", "bro", "dude", "guy", "guys", "people",
    "think", "make", "made", "makes", "making", "just", "really", "actually", "even",
    "much", "many", "good", "bad", "thing", "things", "get", "got", "know", "see",
    "https", "http", "com", "www", "sub", "subscribe", "subscribed", "content",
}


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


def _extract_phrases_from_text(text: str) -> List[str]:
    """Extracts candidate unigrams and bigrams from raw text, filtering stopwords."""
    clean = re.sub(r"https?://\S+", "", text.lower())
    words = re.findall(r"\b[a-z]{3,20}\b", clean)
    phrases: List[str] = []

    # Unigrams
    meaningful_words = [w for w in words if w not in STOPWORDS]
    phrases.extend(meaningful_words)

    # Bigrams
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if w1 not in STOPWORDS and w2 not in STOPWORDS:
            phrases.append(f"{w1} {w2}")

    return phrases


def extract_sentiment_drivers(
    analyzed_items: List[CommentItem],
    category: SentimentCategory,
    top_n: int = 5,
) -> List[SentimentDriverItem]:
    """
    Identifies top key phrases associated with a given sentiment category (praise vs dislike drivers)
    and attaches a representative comment snippet for each.
    """
    category_items = [item for item in analyzed_items if item.sentiment == category and item.text]
    if not category_items:
        return []

    phrase_counter: Counter = Counter()
    phrase_snippets: Dict[str, str] = {}

    for item in category_items:
        text = item.text.strip()
        phrases = _extract_phrases_from_text(text)
        # Avoid counting multiple instances of same phrase in one comment
        unique_phrases = set(phrases)
        for p in unique_phrases:
            phrase_counter[p] += 1
            if p not in phrase_snippets:
                # Capture short snippet
                snippet = text if len(text) <= 90 else f"{text[:87]}..."
                phrase_snippets[p] = snippet

    top_phrases = phrase_counter.most_common(top_n * 2)
    drivers: List[SentimentDriverItem] = []
    seen_roots = set()

    for phrase, count in top_phrases:
        # Prevent near-duplicate bigram/unigram overlap (e.g. "clickbait" and "clickbait title")
        root = phrase.split()[0]
        if root in seen_roots and len(phrase.split()) > 1:
            continue
        seen_roots.add(root)

        drivers.append(
            SentimentDriverItem(
                keyword=phrase,
                count=count,
                sentiment=category,
                sample_snippet=phrase_snippets.get(phrase),
            )
        )
        if len(drivers) >= top_n:
            break

    return drivers


def compute_score_distribution(analyzed_items: List[CommentItem]) -> List[ScoreBucket]:
    """Computes a 5-bucket distribution histogram of compound scores."""
    buckets = [
        {"label": "Very Negative", "range": "[-1.0, -0.6]", "min": -1.0, "max": -0.6, "count": 0},
        {"label": "Leaning Negative", "range": "[-0.6, -0.05]", "min": -0.6, "max": -0.05, "count": 0},
        {"label": "Neutral", "range": "[-0.05, +0.05]", "min": -0.05, "max": 0.05, "count": 0},
        {"label": "Leaning Positive", "range": "[+0.05, +0.6]", "min": 0.05, "max": 0.6, "count": 0},
        {"label": "Very Positive", "range": "[+0.6, +1.0]", "min": 0.6, "max": 1.0, "count": 0},
    ]

    total = len(analyzed_items)
    for item in analyzed_items:
        score = item.sentiment_score if item.sentiment_score is not None else 0.0
        if score < -0.6:
            buckets[0]["count"] += 1
        elif score < -0.05:
            buckets[1]["count"] += 1
        elif score <= 0.05:
            buckets[2]["count"] += 1
        elif score <= 0.6:
            buckets[3]["count"] += 1
        else:
            buckets[4]["count"] += 1

    return [
        ScoreBucket(
            label=b["label"],
            range_label=b["range"],
            count=b["count"],
            percentage=round((b["count"] / total) * 100.0, 1) if total > 0 else 0.0,
        )
        for b in buckets
    ]


def compute_like_weighted_metrics(analyzed_items: List[CommentItem]) -> LikeWeightedMetrics:
    """Computes sentiment metrics weighted by comment community likes."""
    total = len(analyzed_items)
    if total == 0:
        return LikeWeightedMetrics()

    total_weight = 0
    pos_weight = 0
    neu_weight = 0
    neg_weight = 0
    weighted_compound_sum = 0.0

    for item in analyzed_items:
        # Base weight 1 so 0-like comments still count, plus like count
        w = max(item.likes or 0, 0) + 1
        total_weight += w

        compound = item.sentiment_score or 0.0
        weighted_compound_sum += compound * w

        if item.sentiment == SentimentCategory.POSITIVE:
            pos_weight += w
        elif item.sentiment == SentimentCategory.NEGATIVE:
            neg_weight += w
        else:
            neu_weight += w

    if total_weight > 0:
        return LikeWeightedMetrics(
            weighted_compound=round(weighted_compound_sum / total_weight, 4),
            weighted_positive_pct=round((pos_weight / total_weight) * 100.0, 1),
            weighted_neutral_pct=round((neu_weight / total_weight) * 100.0, 1),
            weighted_negative_pct=round((neg_weight / total_weight) * 100.0, 1),
            total_weight=total_weight,
        )
    return LikeWeightedMetrics()


def compute_controversy_index(
    positive_count: int,
    negative_count: int,
    total: int,
    compound_scores: List[float],
) -> Tuple[float, str]:
    """
    Computes a Controversy Index (0.0 to 100.0) measuring audience polarization.
    Returns (controversy_index, controversy_level).
    """
    if total == 0:
        return 0.0, "Low / Consensus"

    pos_ratio = positive_count / total
    neg_ratio = negative_count / total

    # Balance factor: highest when pos and neg are balanced (50/50)
    if (pos_ratio + neg_ratio) > 0:
        balance = 1.0 - abs(pos_ratio - neg_ratio) / (pos_ratio + neg_ratio)
    else:
        balance = 0.0

    # Polarity magnitude: how much of the audience is opinionated vs neutral
    magnitude = min(pos_ratio + neg_ratio, 1.0)

    # Standard deviation of compound scores
    if len(compound_scores) > 1:
        mean_score = sum(compound_scores) / len(compound_scores)
        variance = sum((s - mean_score) ** 2 for s in compound_scores) / len(compound_scores)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0.0

    # Combine: 70% balance * magnitude + 30% score standard deviation
    raw_ci = (balance * magnitude * 70.0) + (std_dev * 30.0)
    controversy_index = round(min(100.0, max(0.0, raw_ci)), 1)

    if controversy_index < 25.0:
        level = "Low / Consensus"
    elif controversy_index < 50.0:
        level = "Moderate"
    elif controversy_index < 75.0:
        level = "Elevated Debate"
    else:
        level = "Intense Polarization"

    return controversy_index, level


def build_diagnostic_verdict(
    total: int,
    pos_pct: float,
    neu_pct: float,
    neg_pct: float,
    controversy_index: float,
    controversy_level: str,
    weighted: LikeWeightedMetrics,
) -> DiagnosticVerdict:
    """Builds an executive diagnostic verdict based on reconciled metrics."""
    if total == 0:
        return DiagnosticVerdict(
            label="Zero Comments Available",
            headline="No accessible public comments were available to evaluate audience sentiment.",
            severity="info",
            controversy_index=0.0,
            controversy_level="Low / Consensus",
        )

    # 1. Polarized Debate (Check first when both positive and negative factions are prominent)
    if controversy_index >= 50.0 and pos_pct >= 25.0 and neg_pct >= 25.0:
        return DiagnosticVerdict(
            label="Polarized Community Debate",
            headline=f"The audience is sharply split ({pos_pct}% positive vs {neg_pct}% negative) with high controversy ({controversy_index}/100).",
            severity="warning",
            controversy_index=controversy_index,
            controversy_level=controversy_level,
        )

    # 2. Severe Backlash (Negative heavily dominates without offsetting positive debate)
    if neg_pct >= 45.0 or (neg_pct >= 35.0 and weighted.weighted_negative_pct >= 50.0):
        return DiagnosticVerdict(
            label="Severe Audience Backlash",
            headline=f"Critical reactions dominate ({neg_pct}% negative) with strong community upvoting on negative feedback.",
            severity="critical",
            controversy_index=controversy_index,
            controversy_level=controversy_level,
        )

    # 3. Elevated Negative Friction
    if neg_pct >= 30.0:
        return DiagnosticVerdict(
            label="Elevated Audience Friction",
            headline=f"Notable volume of critical responses ({neg_pct}% negative) highlighting audience dissatisfaction.",
            severity="warning",
            controversy_index=controversy_index,
            controversy_level=controversy_level,
        )

    # 4. Overwhelming Praise
    if pos_pct >= 75.0:
        return DiagnosticVerdict(
            label="Overwhelming Audience Praise",
            headline=f"Exceptionally positive audience reception ({pos_pct}% positive) with minimal critical pushback.",
            severity="success",
            controversy_index=controversy_index,
            controversy_level=controversy_level,
        )

    # 5. Favorable Reception
    if pos_pct >= 50.0:
        return DiagnosticVerdict(
            label="Favorable Reception",
            headline=f"Positive sentiment noticeably outweighs criticism ({pos_pct}% positive vs {neg_pct}% negative).",
            severity="success",
            controversy_index=controversy_index,
            controversy_level=controversy_level,
        )

    # 6. Balanced / Neutral Consensus
    return DiagnosticVerdict(
        label="Balanced / Neutral Consensus",
        headline="Audience reaction is largely composed of neutral or evenly balanced commentary.",
        severity="info",
        controversy_index=controversy_index,
        controversy_level=controversy_level,
    )


def analyze_comments_batch(
    raw_comments: List[CommentItem],
) -> Tuple[List[CommentItem], SentimentSummary]:
    """
    Processes a list of CommentItems, filtering out items without usable text,
    assigning sentiment classification, extracting drivers, computing score distribution,
    like-weighted resonance, and controversy index into a strictly reconciled SentimentSummary.
    """
    analyzed_items: List[CommentItem] = []
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    compound_sum = 0.0
    compound_scores: List[float] = []

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
        compound_scores.append(compound)
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

    # 1. Dislike and Praise Driver extraction
    praise_drivers = extract_sentiment_drivers(analyzed_items, SentimentCategory.POSITIVE, top_n=5)
    dislike_drivers = extract_sentiment_drivers(analyzed_items, SentimentCategory.NEGATIVE, top_n=5)

    # 2. Score distribution histogram
    score_dist = compute_score_distribution(analyzed_items)

    # 3. Like-weighted community resonance
    like_weighted = compute_like_weighted_metrics(analyzed_items)

    # 4. Controversy Index
    controversy_index, controversy_level = compute_controversy_index(
        positive_count, negative_count, total, compound_scores
    )

    # 5. Executive diagnostic verdict
    verdict = build_diagnostic_verdict(
        total=total,
        pos_pct=pos_pct,
        neu_pct=neu_pct,
        neg_pct=neg_pct,
        controversy_index=controversy_index,
        controversy_level=controversy_level,
        weighted=like_weighted,
    )

    summary = SentimentSummary(
        positive_count=positive_count,
        neutral_count=neutral_count,
        negative_count=negative_count,
        total_analyzed=total,
        positive_percentage=pos_pct,
        neutral_percentage=neu_pct,
        negative_percentage=neg_pct,
        average_compound=avg_comp,
        dislike_drivers=dislike_drivers,
        praise_drivers=praise_drivers,
        score_distribution=score_dist,
        like_weighted=like_weighted,
        verdict=verdict,
    )

    return analyzed_items, summary


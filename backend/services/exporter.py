import io
import csv
import json
from backend.models.schemas import AnalysisResult


def export_analysis_json(result: AnalysisResult) -> str:
    """Exports full analysis report and comments to formatted JSON."""
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)


def export_analysis_csv(result: AnalysisResult) -> str:
    """
    Exports analysis report and individual analyzed comments to a cleanly structured CSV.
    Includes metadata, diagnostics, sentiment summary, and comment details.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Report Overview
    writer.writerow(["# DISLIKESCOPE-AI ANALYSIS REPORT"])
    writer.writerow(["Report ID", result.id])
    writer.writerow(["Platform", result.platform.value if hasattr(result.platform, "value") else str(result.platform)])
    writer.writerow(["Target ID", result.target_id])
    writer.writerow(["Title", result.title or "N/A"])
    writer.writerow(["Author/Channel", result.author or "N/A"])
    writer.writerow(["URL", result.url])
    writer.writerow(["Analyzed At", result.created_at])
    writer.writerow(["Methodology", result.methodology])
    writer.writerow([])

    # 2. Retrieval Diagnostics
    writer.writerow(["# RETRIEVAL DIAGNOSTICS"])
    diag = result.diagnostics
    writer.writerow(["Reported Comment Count", diag.reported_comment_count if diag.reported_comment_count is not None else "N/A"])
    writer.writerow(["Retrieved Records Count", diag.retrieved_records_count])
    writer.writerow(["Usable Text Count", diag.usable_text_count])
    writer.writerow(["Successfully Analyzed Count", diag.analyzed_count])
    writer.writerow(["Extraction Status", diag.extraction_status])
    writer.writerow(["Comments Disabled", diag.comments_disabled])
    writer.writerow(["Failure/Empty Reason", diag.failure_reason or "None"])
    writer.writerow(["Limitations Note", diag.limitations_note or "None"])
    writer.writerow([])

    # 3. Sentiment Summary & Advanced Diagnostics
    writer.writerow(["# SENTIMENT SUMMARY & ADVANCED DIAGNOSTICS"])
    sent = result.sentiment
    if sent.verdict:
        writer.writerow(["Executive Verdict", sent.verdict.label])
        writer.writerow(["Verdict Summary", sent.verdict.headline])
        writer.writerow(["Controversy Index", f"{sent.verdict.controversy_index}/100 ({sent.verdict.controversy_level})"])
    writer.writerow(["Metric", "Count", "Percentage"])
    writer.writerow(["Positive (Raw)", sent.positive_count, f"{sent.positive_percentage}%"])
    writer.writerow(["Neutral (Raw)", sent.neutral_count, f"{sent.neutral_percentage}%"])
    writer.writerow(["Negative (Raw)", sent.negative_count, f"{sent.negative_percentage}%"])
    writer.writerow(["Total Analyzed", sent.total_analyzed, "100.0%"])
    writer.writerow(["Average Compound Score", sent.average_compound, "N/A"])

    if sent.like_weighted:
        writer.writerow([])
        writer.writerow(["# COMMUNITY LIKE-WEIGHTED SENTIMENT"])
        writer.writerow(["Metric", "Weighted Percentage"])
        writer.writerow(["Positive (Weighted)", f"{sent.like_weighted.weighted_positive_pct}%"])
        writer.writerow(["Neutral (Weighted)", f"{sent.like_weighted.weighted_neutral_pct}%"])
        writer.writerow(["Negative (Weighted)", f"{sent.like_weighted.weighted_negative_pct}%"])
        writer.writerow(["Weighted Compound Score", sent.like_weighted.weighted_compound])

    if sent.praise_drivers:
        writer.writerow([])
        writer.writerow(["# TOP PRAISE DRIVERS"])
        writer.writerow(["Theme/Phrase", "Mentions", "Representative Sample"])
        for d in sent.praise_drivers:
            writer.writerow([d.keyword, d.count, (d.sample_snippet or "").replace("\r\n", " ").replace("\n", " ")])

    if sent.dislike_drivers:
        writer.writerow([])
        writer.writerow(["# TOP DISLIKE DRIVERS"])
        writer.writerow(["Theme/Phrase", "Mentions", "Representative Sample"])
        for d in sent.dislike_drivers:
            writer.writerow([d.keyword, d.count, (d.sample_snippet or "").replace("\r\n", " ").replace("\n", " ")])

    writer.writerow([])

    # 4. Engagement Metrics
    writer.writerow(["# ENGAGEMENT METRICS"])
    eng = result.engagement
    writer.writerow(["Views", eng.views if eng.views is not None else "N/A"])
    writer.writerow(["Likes", eng.likes if eng.likes is not None else "N/A"])
    writer.writerow(["Comments/Replies", eng.comments if eng.comments is not None else "N/A"])
    if eng.third_party_dislikes:
        writer.writerow(["Estimated Dislikes (3rd-Party)", eng.third_party_dislikes.estimated_dislikes])
        writer.writerow(["Dislike Estimate Source", eng.third_party_dislikes.source])
        writer.writerow(["Dislike Disclaimer", eng.third_party_dislikes.limitations_note])
    writer.writerow([])

    # 5. Comment Level Data
    writer.writerow(["# ANALYZED COMMENTS SAMPLE"])
    writer.writerow(["Comment ID", "Author", "Published At", "Likes", "Assigned Sentiment", "Compound Score", "Text"])
    for c in result.comments_sample:
        writer.writerow([
            c.id,
            c.author,
            c.published_at or "",
            c.likes or 0,
            c.sentiment.value if c.sentiment else "N/A",
            c.sentiment_score if c.sentiment_score is not None else "",
            (c.text or "").replace("\r\n", " ").replace("\n", " "),
        ])

    return output.getvalue()

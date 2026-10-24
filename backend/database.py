import sqlite3
import json
import logging
from typing import List, Optional
from backend import config
from backend.models.schemas import (
    AnalysisResult,
    HistorySummary,
    SentimentSummary,
    EngagementMetrics,
    RetrievalDiagnostics,
    CommentItem,
    PlatformType,
)

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(config.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                url TEXT NOT NULL,
                target_id TEXT NOT NULL,
                title TEXT,
                author TEXT,
                thumbnail_url TEXT,
                created_at TEXT NOT NULL,
                sentiment_json TEXT NOT NULL,
                engagement_json TEXT NOT NULL,
                diagnostics_json TEXT NOT NULL,
                methodology TEXT NOT NULL,
                comments_sample_json TEXT NOT NULL
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_platform ON analyses(platform);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);")
        conn.commit()
    logger.info("Database initialized successfully at %s", config.DATABASE_PATH)


def save_analysis(result: AnalysisResult) -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO analyses (
                id, platform, url, target_id, title, author, thumbnail_url,
                created_at, sentiment_json, engagement_json, diagnostics_json,
                methodology, comments_sample_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.id,
                result.platform.value if hasattr(result.platform, "value") else str(result.platform),
                result.url,
                result.target_id,
                result.title,
                result.author,
                result.thumbnail_url,
                result.created_at,
                json.dumps(result.sentiment.model_dump()),
                json.dumps(result.engagement.model_dump()),
                json.dumps(result.diagnostics.model_dump()),
                result.methodology,
                json.dumps([c.model_dump() for c in result.comments_sample]),
            ),
        )
        conn.commit()


def get_analysis(analysis_id: str) -> Optional[AnalysisResult]:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
        if not row:
            return None

        sentiment_data = json.loads(row["sentiment_json"])
        engagement_data = json.loads(row["engagement_json"])
        diagnostics_data = json.loads(row["diagnostics_json"])
        comments_data = json.loads(row["comments_sample_json"])
        comments_items = [CommentItem(**c) for c in comments_data]

        sentiment_summary = SentimentSummary(**sentiment_data)
        # Backward compatibility: dynamically enrich legacy records missing advanced analytics
        if sentiment_summary.verdict is None and comments_items:
            from backend.services.sentiment import (
                extract_sentiment_drivers,
                compute_score_distribution,
                compute_like_weighted_metrics,
                compute_controversy_index,
                build_diagnostic_verdict,
            )
            from backend.models.schemas import SentimentCategory
            if not sentiment_summary.praise_drivers:
                sentiment_summary.praise_drivers = extract_sentiment_drivers(comments_items, SentimentCategory.POSITIVE, top_n=5)
            if not sentiment_summary.dislike_drivers:
                sentiment_summary.dislike_drivers = extract_sentiment_drivers(comments_items, SentimentCategory.NEGATIVE, top_n=5)
            if not sentiment_summary.score_distribution:
                sentiment_summary.score_distribution = compute_score_distribution(comments_items)
            if not sentiment_summary.like_weighted:
                sentiment_summary.like_weighted = compute_like_weighted_metrics(comments_items)

            ci, cl = compute_controversy_index(
                sentiment_summary.positive_count,
                sentiment_summary.negative_count,
                sentiment_summary.total_analyzed,
                [c.sentiment_score for c in comments_items if c.sentiment_score is not None],
            )
            sentiment_summary.verdict = build_diagnostic_verdict(
                total=sentiment_summary.total_analyzed,
                pos_pct=sentiment_summary.positive_percentage,
                neu_pct=sentiment_summary.neutral_percentage,
                neg_pct=sentiment_summary.negative_percentage,
                controversy_index=ci,
                controversy_level=cl,
                weighted=sentiment_summary.like_weighted,
            )

        return AnalysisResult(
            id=row["id"],
            platform=PlatformType(row["platform"]),
            url=row["url"],
            target_id=row["target_id"],
            title=row["title"],
            author=row["author"],
            thumbnail_url=row["thumbnail_url"],
            created_at=row["created_at"],
            sentiment=sentiment_summary,
            engagement=EngagementMetrics(**engagement_data),
            diagnostics=RetrievalDiagnostics(**diagnostics_data),
            methodology=row["methodology"],
            comments_sample=comments_items,
        )


def list_analyses(limit: int = 50, offset: int = 0) -> List[HistorySummary]:
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, platform, url, target_id, title, author, created_at,
                   sentiment_json, diagnostics_json
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

        summaries = []
        for r in rows:
            sentiment_data = json.loads(r["sentiment_json"])
            diagnostics_data = json.loads(r["diagnostics_json"])
            summaries.append(
                HistorySummary(
                    id=r["id"],
                    platform=PlatformType(r["platform"]),
                    url=r["url"],
                    target_id=r["target_id"],
                    title=r["title"],
                    author=r["author"],
                    created_at=r["created_at"],
                    total_analyzed=sentiment_data.get("total_analyzed", 0),
                    positive_count=sentiment_data.get("positive_count", 0),
                    neutral_count=sentiment_data.get("neutral_count", 0),
                    negative_count=sentiment_data.get("negative_count", 0),
                    extraction_status=diagnostics_data.get("extraction_status", "unknown"),
                )
            )
        return summaries


def delete_analysis(analysis_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0

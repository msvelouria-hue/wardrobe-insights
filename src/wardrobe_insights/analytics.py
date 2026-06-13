from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3


@dataclass(frozen=True)
class ItemScore:
    item_id: str
    category: str
    color: str | None
    wear_count: int
    last_worn_at: str | None
    loves: int
    dislikes: int
    freshness_score: float


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _days_since(value: str | None, *, now: datetime) -> int | None:
    parsed = _parse_datetime(value)
    if parsed is None:
        return None
    return max((now - parsed).days, 0)


def recommend_refresh_items(
    conn: sqlite3.Connection,
    user_id: str,
    *,
    limit: int = 5,
    now: datetime | None = None,
) -> list[ItemScore]:
    """Rank active closet items that are good candidates to reintroduce."""

    if limit <= 0:
        return []

    current_time = now or datetime.now(timezone.utc)
    rows = conn.execute(
        """
        SELECT
            ci.id AS item_id,
            ci.category,
            ci.color,
            COUNT(DISTINCT oi.outfit_id) AS wear_count,
            MAX(o.worn_at) AS last_worn_at,
            SUM(CASE WHEN f.signal = 'love' THEN 1 ELSE 0 END) AS loves,
            SUM(CASE WHEN f.signal = 'dislike' THEN 1 ELSE 0 END) AS dislikes
        FROM closet_items ci
        LEFT JOIN outfit_items oi ON oi.item_id = ci.id
        LEFT JOIN outfits o ON o.id = oi.outfit_id
        LEFT JOIN item_feedback f ON f.item_id = ci.id
        WHERE ci.user_id = ? AND ci.active = 1
        GROUP BY ci.id
        """,
        (user_id,),
    ).fetchall()

    scored: list[ItemScore] = []
    for row in rows:
        days = _days_since(row["last_worn_at"], now=current_time)
        freshness = 100.0 if days is None else min(float(days), 60.0)
        preference = (row["loves"] or 0) * 3.0 - (row["dislikes"] or 0) * 8.0
        underuse_bonus = 10.0 if row["wear_count"] == 0 else 0.0
        score = freshness + preference + underuse_bonus

        scored.append(
            ItemScore(
                item_id=row["item_id"],
                category=row["category"],
                color=row["color"],
                wear_count=row["wear_count"],
                last_worn_at=row["last_worn_at"],
                loves=row["loves"] or 0,
                dislikes=row["dislikes"] or 0,
                freshness_score=round(score, 2),
            )
        )

    return sorted(
        scored,
        key=lambda item: (item.freshness_score, -item.wear_count, item.item_id),
        reverse=True,
    )[:limit]


def category_coverage(conn: sqlite3.Connection, user_id: str) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT category, COUNT(*) AS item_count
        FROM closet_items
        WHERE user_id = ? AND active = 1
        GROUP BY category
        ORDER BY category
        """,
        (user_id,),
    ).fetchall()

    return {row["category"]: row["item_count"] for row in rows}

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from importlib.resources import files
import sqlite3
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize(conn: sqlite3.Connection) -> None:
    schema = files("wardrobe_insights").joinpath("schema.sql").read_text()
    conn.executescript(schema)
    conn.commit()


def upsert_user(conn: sqlite3.Connection, user_id: str, email: str | None = None) -> None:
    conn.execute(
        """
        INSERT INTO users (id, email, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET email = excluded.email
        """,
        (user_id, email, utc_now()),
    )
    conn.commit()


def add_closet_item(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    item_id: str,
    category: str,
    color: str | None = None,
    material: str | None = None,
    season: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO closet_items (
            id, user_id, category, color, material, season, active, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (item_id, user_id, category, color, material, season, utc_now()),
    )
    conn.commit()


def record_outfit(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    outfit_id: str | None = None,
    item_roles: Iterable[tuple[str, str]],
    worn_at: str,
    weather_temp_f: int | None = None,
    occasion: str | None = None,
    rating: int | None = None,
) -> str:
    resolved_outfit_id = outfit_id or f"outfit_{uuid4().hex[:12]}"
    item_role_list = list(item_roles)

    if not item_role_list:
        raise ValueError("record_outfit requires at least one item")

    with conn:
        conn.execute(
            """
            INSERT INTO outfits (
                id, user_id, worn_at, weather_temp_f, occasion, rating
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (resolved_outfit_id, user_id, worn_at, weather_temp_f, occasion, rating),
        )
        conn.executemany(
            """
            INSERT INTO outfit_items (outfit_id, item_id, role)
            VALUES (?, ?, ?)
            """,
            [
                (resolved_outfit_id, item_id, role)
                for item_id, role in item_role_list
            ],
        )

    return resolved_outfit_id


def record_feedback(
    conn: sqlite3.Connection,
    *,
    item_id: str,
    signal: str,
    reason: str | None = None,
) -> None:
    if signal not in {"love", "dislike"}:
        raise ValueError("signal must be 'love' or 'dislike'")

    conn.execute(
        """
        INSERT INTO item_feedback (item_id, signal, reason, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (item_id, signal, reason, utc_now()),
    )
    conn.commit()


def rows(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    return list(conn.execute(sql, params))

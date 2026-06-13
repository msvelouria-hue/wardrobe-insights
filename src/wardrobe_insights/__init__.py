"""Wardrobe usage analytics with a small SQLite-backed data model."""

from .analytics import ItemScore, category_coverage, recommend_refresh_items
from .db import add_closet_item, connect, initialize, record_feedback, record_outfit

__all__ = [
    "ItemScore",
    "add_closet_item",
    "category_coverage",
    "connect",
    "initialize",
    "recommend_refresh_items",
    "record_feedback",
    "record_outfit",
]

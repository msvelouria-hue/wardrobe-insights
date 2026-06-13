from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wardrobe_insights.analytics import category_coverage, recommend_refresh_items
from wardrobe_insights.db import (
    add_closet_item,
    connect,
    initialize,
    record_feedback,
    record_outfit,
    upsert_user,
)


class WardrobeInsightsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = connect()
        initialize(self.conn)
        upsert_user(self.conn, "user_1", "sabrina@example.com")

        add_closet_item(
            self.conn,
            user_id="user_1",
            item_id="silk_blouse",
            category="Tops",
            color="ivory",
            material="silk",
            season="spring",
        )
        add_closet_item(
            self.conn,
            user_id="user_1",
            item_id="black_trousers",
            category="Bottoms",
            color="black",
            material="wool",
            season="fall",
        )
        add_closet_item(
            self.conn,
            user_id="user_1",
            item_id="silver_flats",
            category="Shoes",
            color="silver",
            material="leather",
            season="spring",
        )

    def test_category_coverage_counts_active_items(self) -> None:
        self.assertEqual(
            category_coverage(self.conn, "user_1"),
            {"Bottoms": 1, "Shoes": 1, "Tops": 1},
        )

    def test_refresh_recommendations_prioritize_unworn_items(self) -> None:
        now = datetime(2026, 6, 13, tzinfo=timezone.utc)
        record_outfit(
            self.conn,
            user_id="user_1",
            outfit_id="outfit_recent",
            item_roles=[("silk_blouse", "top"), ("black_trousers", "bottom")],
            worn_at=(now - timedelta(days=1)).isoformat(),
            weather_temp_f=68,
            occasion="class",
            rating=1,
        )

        recommendations = recommend_refresh_items(self.conn, "user_1", now=now)

        self.assertEqual(recommendations[0].item_id, "silver_flats")
        self.assertEqual(recommendations[0].wear_count, 0)

    def test_disliked_items_are_penalized(self) -> None:
        now = datetime(2026, 6, 13, tzinfo=timezone.utc)
        record_feedback(self.conn, item_id="silver_flats", signal="dislike", reason="pinches")
        record_feedback(self.conn, item_id="silk_blouse", signal="love", reason="easy to style")

        recommendations = recommend_refresh_items(self.conn, "user_1", now=now, limit=3)
        ordered_ids = [item.item_id for item in recommendations]

        self.assertLess(
            ordered_ids.index("silver_flats"),
            3,
            "disliked but unworn items can still appear, just with a lower score",
        )
        self.assertGreater(
            next(item for item in recommendations if item.item_id == "silk_blouse").freshness_score,
            0,
        )


if __name__ == "__main__":
    unittest.main()

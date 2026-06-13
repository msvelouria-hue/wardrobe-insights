from __future__ import annotations

import argparse
from pathlib import Path

from .analytics import category_coverage, recommend_refresh_items
from .db import connect, initialize


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze wardrobe usage data.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="Create or migrate a database.")
    init_parser.add_argument("database", type=Path)

    coverage_parser = subcommands.add_parser("coverage", help="Print item counts by category.")
    coverage_parser.add_argument("database", type=Path)
    coverage_parser.add_argument("user_id")

    refresh_parser = subcommands.add_parser("refresh", help="Print refresh recommendations.")
    refresh_parser.add_argument("database", type=Path)
    refresh_parser.add_argument("user_id")
    refresh_parser.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()
    conn = connect(str(args.database))

    if args.command == "init":
        initialize(conn)
        print(f"Initialized {args.database}")
        return

    if args.command == "coverage":
        for category, count in category_coverage(conn, args.user_id).items():
            print(f"{category}: {count}")
        return

    if args.command == "refresh":
        for item in recommend_refresh_items(conn, args.user_id, limit=args.limit):
            print(
                f"{item.item_id}\t{item.category}\t"
                f"score={item.freshness_score}\twears={item.wear_count}"
            )


if __name__ == "__main__":
    main()

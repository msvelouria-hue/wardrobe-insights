# Wardrobe Insights

A compact Python data project for analyzing wardrobe usage, outfit history, and item freshness from a normalized SQLite schema.

This repo is intentionally small: it demonstrates clean Python domain logic, a real relational schema, a testable data access layer, and a local development path that works without external services.

## What This Shows

- Python 3.9+ project structure with `src/` layout
- SQLite schema with foreign keys, join tables, and indexes
- Repository-style data access functions
- Deterministic wardrobe analytics logic
- CLI entry point for local workflows
- Unit tests that run without network access

## Architecture

```text
wardrobe-insights/
├── src/wardrobe_insights/
│   ├── schema.sql          # SQLite schema
│   ├── db.py               # Connection, migrations, inserts, and queries
│   ├── analytics.py        # Freshness scoring and coverage analysis
│   └── cli.py              # Local command-line entry point
├── tests/
│   └── test_analytics.py   # End-to-end tests over an in-memory database
└── pyproject.toml
```

## Architecture Decisions

- **SQLite first**: SQLite keeps the project simple to run while still forcing real schema design and relational thinking.
- **Normalized outfit history**: Outfits and closet items are connected through `outfit_items`, so a single outfit can contain many items and each item can appear in many outfits.
- **Analytics separate from storage**: `db.py` owns persistence; `analytics.py` owns scoring. That makes the recommendation logic easy to test without rewriting database helpers.
- **No hidden services**: The project does not require cloud credentials, API keys, or a running server.

## Database Schema

```text
users
├── id TEXT PRIMARY KEY
├── email TEXT UNIQUE
└── created_at TEXT NOT NULL

closet_items
├── id TEXT PRIMARY KEY
├── user_id TEXT NOT NULL -> users.id
├── category TEXT NOT NULL
├── color TEXT
├── material TEXT
├── season TEXT
├── active INTEGER NOT NULL DEFAULT 1
└── created_at TEXT NOT NULL

outfits
├── id TEXT PRIMARY KEY
├── user_id TEXT NOT NULL -> users.id
├── worn_at TEXT NOT NULL
├── weather_temp_f INTEGER
├── occasion TEXT
└── rating INTEGER

outfit_items
├── outfit_id TEXT NOT NULL -> outfits.id
├── item_id TEXT NOT NULL -> closet_items.id
├── role TEXT NOT NULL
└── PRIMARY KEY (outfit_id, item_id)

item_feedback
├── id INTEGER PRIMARY KEY AUTOINCREMENT
├── item_id TEXT NOT NULL -> closet_items.id
├── signal TEXT NOT NULL CHECK (signal IN ('love', 'dislike'))
├── reason TEXT
└── created_at TEXT NOT NULL
```

Indexes support the common queries for a user's closet, outfit history, and item feedback.

## Local Development

```bash
git clone <repository-url>
cd wardrobe-insights
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest
```

## CLI Usage

Create a local database:

```bash
python -m wardrobe_insights.cli init wardrobe.sqlite
```

Print category coverage:

```bash
python -m wardrobe_insights.cli coverage wardrobe.sqlite user_1
```

Print refresh recommendations:

```bash
python -m wardrobe_insights.cli refresh wardrobe.sqlite user_1 --limit 5
```

## Example Use Case

The freshness scorer ranks active closet items by:

- whether they have never been worn
- how many days have passed since last wear
- positive and negative item feedback
- category coverage across the closet

That makes it useful as a small companion service or data-analysis layer for wardrobe apps that want transparent, testable recommendation behavior.

## Quality Checks

```bash
python -m unittest
python -m compileall src tests
```

## License

MIT

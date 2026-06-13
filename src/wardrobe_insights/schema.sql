PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS closet_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    color TEXT,
    material TEXT,
    season TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outfits (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    worn_at TEXT NOT NULL,
    weather_temp_f INTEGER,
    occasion TEXT,
    rating INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outfit_items (
    outfit_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    role TEXT NOT NULL,
    PRIMARY KEY (outfit_id, item_id),
    FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES closet_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS item_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    signal TEXT NOT NULL CHECK (signal IN ('love', 'dislike')),
    reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES closet_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_closet_items_user_category
    ON closet_items (user_id, category);

CREATE INDEX IF NOT EXISTS idx_outfits_user_worn_at
    ON outfits (user_id, worn_at DESC);

CREATE INDEX IF NOT EXISTS idx_outfit_items_item
    ON outfit_items (item_id);

CREATE INDEX IF NOT EXISTS idx_item_feedback_item_signal
    ON item_feedback (item_id, signal);

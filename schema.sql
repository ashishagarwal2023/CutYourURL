CREATE TABLE IF NOT EXISTS short_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_url TEXT UNIQUE,
    original_url TEXT
);

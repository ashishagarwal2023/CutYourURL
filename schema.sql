CREATE TABLE IF NOT EXISTS short_urls
(
	id           INTEGER PRIMARY KEY AUTOINCREMENT,
	short_url    TEXT UNIQUE,
	original_url TEXT,
	views        INTEGER   DEFAULT 0,
	length       INTEGER GENERATED ALWAYS AS (LENGTH(short_url)) STORED,
	inserted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	captcha      INTEGER   DEFAULT 0
);

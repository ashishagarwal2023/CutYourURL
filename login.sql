CREATE TABLE users (
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT,
	otp          INTEGER,
	otp_sent_at  INTEGER
);

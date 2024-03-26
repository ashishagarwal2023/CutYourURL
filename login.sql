CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT,
    verified BOOLEAN DEFAULT FALSE,
    OTP INTEGER
);

CREATE TABLE users (
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT,
    verified BOOLEAN DEFAULT FALSE,
    OTP INTEGER
);

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
);

-- Create the messages table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT,
    response TEXT
);

-- Insert Marty's login credentials
INSERT OR IGNORE INTO users (username, password) VALUES ('marty', 'password123');

-- Insert Doc's login credentials
INSERT OR IGNORE INTO users (username, password) VALUES ('doc', 'greatscott!');


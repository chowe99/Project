-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
);

-- Insert Marty's login credentials
INSERT OR IGNORE INTO users (username, password) VALUES ('marty', 'password123');

-- Insert Doc's login credentials
INSERT OR IGNORE INTO users (username, password) VALUES ('doc', 'greatscott!');

-- Create the messages table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT,
    response TEXT
);

-- Insert placeholder messages
INSERT INTO messages (sender, message, response) VALUES ('marty', 'Hi Doc!', 'Got your message, Marty!');
INSERT INTO messages (sender, message, response) VALUES ('marty', 'Whats going on?', 'Dont worry, Marty! Well fix the timeline.');


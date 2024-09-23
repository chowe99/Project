-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- Insert sample data
INSERT INTO users (name, email) VALUES ('Marty McFly', 'marty@mcfly.com');
INSERT INTO users (name, email) VALUES ('Doc Brown', 'doc@brown.com');
INSERT INTO users (name, email) VALUES ('Biff Tannen', 'biff@tannen.com');

-- Create secrets table
CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flag TEXT NOT NULL
);

-- Insert the flag
INSERT INTO secrets (flag) VALUES ('FLAG{GreatScott_1.21_Gigawatts}');


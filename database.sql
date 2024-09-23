CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO users (id, name) VALUES (1, 'Alice');
INSERT INTO users (id, name) VALUES (2, 'Bob');
INSERT INTO users (id, name) VALUES (3, 'Charlie');

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    comment TEXT NOT NULL
);

INSERT INTO comments (id, comment) VALUES (1, 'This is a great site!');
INSERT INTO comments (id, comment) VALUES (2, 'Nice work!');


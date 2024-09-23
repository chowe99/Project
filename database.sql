CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);

INSERT INTO users (name, email) VALUES ('Marty McFly', 'marty@mcfly.com');
INSERT INTO users (name, email) VALUES ('Doc Brown', 'doc@brown.com');
INSERT INTO users (name, email) VALUES ('Biff Tannen', 'biff@tannen.com');

CREATE TABLE secrets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flag VARCHAR(255) NOT NULL
);

INSERT INTO secrets (flag) VALUES ('FLAG{GreatScott_1.21_Gigawatts}');


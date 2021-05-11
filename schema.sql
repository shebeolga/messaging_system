CREATE TABLE users (
    id INTEGER PRIMARY KEY autoincrement,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY autoincrement,
    sender INTEGER NOT NULL,
    receiver INTEGER NOT NULL,
    message TEXT NOT NULL,
    subject TEXT,
    creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_date DATETIME,
    read BOOLEAN NOT NULL 0,
    FOREIGN KEY(sender) REFERENCES users(id),
    FOREIGN KEY(receiver) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER,
    type TEXT CHECK(type IN ('book','summary')) NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
);

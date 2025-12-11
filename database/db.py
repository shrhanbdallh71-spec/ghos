import sqlite3

DB_PATH = "database/cybersec_dmu.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        type TEXT CHECK(type IN ('book','summary')) NOT NULL,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    );
    """)
    conn.commit()
    conn.close()

def add_subject(name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def add_resource(subject_name, res_type, title, link):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM subjects WHERE name=?", (subject_name,))
    subject = cur.fetchone()
    if subject:
        subject_id = subject[0]
        cur.execute(
            "INSERT INTO resources (subject_id, type, title, link) VALUES (?, ?, ?, ?)",
            (subject_id, res_type, title, link)
        )
        conn.commit()
    conn.close()

def get_subjects():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM subjects")
    subjects = [row[0] for row in cur.fetchall()]
    conn.close()
    return subjects

def get_resources(subject_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT type, title, link FROM resources
        JOIN subjects ON subjects.id = resources.subject_id
        WHERE subjects.name = ?
    """, (subject_name,))
    data = cur.fetchall()
    conn.close()
    return data

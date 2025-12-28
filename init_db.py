import sqlite3

conn = sqlite3.connect("storage.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    student_name TEXT,
    department TEXT,
    year INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY,
    subject_name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS marks (
    student_id INTEGER,
    subject_id INTEGER,
    marks INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
)
""")

conn.commit()
conn.close()

print("Tables created successfully.")

import sqlite3

conn = sqlite3.connect("storage.db")
cur = conn.cursor()

cur.executemany(
    "INSERT INTO students VALUES (?, ?, ?, ?)",
    [
        (1, "Arjun", "CSE", 3),
        (2, "Meena", "CSE", 3),
        (3, "Rahul", "ECE", 2)
    ]
)

cur.executemany(
    "INSERT INTO subjects VALUES (?, ?)",
    [
        (101, "DBMS"),
        (102, "OS"),
        (103, "CN")
    ]
)

cur.executemany(
    "INSERT INTO marks VALUES (?, ?, ?)",
    [
        (1, 101, 85),
        (1, 102, 78),
        (1, 103, 90),
        (2, 101, 92),
        (2, 102, 88),
        (2, 103, 95),
        (3, 101, 70),
        (3, 102, 65),
        (3, 103, 72)
    ]
)

conn.commit()
conn.close()

print("Data inserted successfully.")

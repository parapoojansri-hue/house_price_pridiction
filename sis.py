import sqlite3

conn = sqlite3.connect("sis.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    course TEXT,
    year INTEGER
)
""")

conn.commit()
conn.close()

print("Database and students table created successfully!")

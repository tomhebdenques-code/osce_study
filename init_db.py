import sqlite3

# 1. Connect to (or create) the database file
connection = sqlite3.connect("osce_platform.db")
cursor = connection.cursor()

# 2. Create the 'attempts' table
# We define exactly what 'columns' we want
cursor.execute("""
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    score INTEGER,
    feedback TEXT,
    transcript TEXT
)
""")

connection.commit()
connection.close()

print("✅ Database initialized: osce_platform.db created.")
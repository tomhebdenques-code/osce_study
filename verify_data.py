import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "osce_platform.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Checking database at: {db_path}")

# Check Attempts
cursor.execute("SELECT id, student_name, score FROM attempts")
rows = cursor.fetchall()

if not rows:
    print("❌ No attempts found in the table.")
else:
    print(f"✅ Found {len(rows)} attempts:")
    for row in rows:
        print(f"ID: {row[0]} | Student: {row[1]} | Score: {row[2]}")

conn.close()
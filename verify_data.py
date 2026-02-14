import sqlite3
import os

#run this after a scenario to verify that the DB is populating

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "osce_platform.db")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print(f"--- DATABASE AUDIT: {db_path} ---")

# Check Scenarios
print("\n[SCENARIOS]")
try:
    cursor.execute("SELECT id, name FROM scenarios")
    scenarios = cursor.fetchall()
    for s in scenarios:
        print(f" - {s['name']} ({s['id']})")
except Exception as e:
    print(f"Error reading scenarios: {e}")

# Check Attempts
print("\n[RECENT ATTEMPTS]")
try:
    cursor.execute("SELECT id, student_name, score, timestamp FROM attempts ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    if not rows:
        print(" -> No attempts recorded yet.")
    else:
        for row in rows:
            print(f" -> ID: {row['id']} | Score: {row['score']}% | Time: {row['timestamp']}")
except Exception as e:
    print(f"Error reading attempts: {e}")

conn.close()
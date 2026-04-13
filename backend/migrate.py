"""
Runs automatically before uvicorn starts.
Creates the table if missing, then adds any missing columns.
"""
import sqlite3, os

# Import database.py first — this runs Base.metadata.create_all()
# which creates the problems table if it doesn't exist yet
import database  # noqa: F401

DB_PATH = os.path.join(os.path.dirname(__file__), "problems.db")
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

cur.execute("PRAGMA table_info(problems)")
existing = [row[1] for row in cur.fetchall()]

new_columns = {
    "image_path":    "TEXT DEFAULT ''",
    "student_name":  "TEXT DEFAULT ''",
    "student_email": "TEXT DEFAULT ''",
    "urgency":       "TEXT DEFAULT 'Medium'",
    "duplicate_of":  "TEXT DEFAULT ''",
}

for col, definition in new_columns.items():
    if col not in existing:
        cur.execute(f"ALTER TABLE problems ADD COLUMN {col} {definition}")
        print(f"✓ Added column: {col}")
    else:
        print(f"  Skipped (already exists): {col}")

conn.commit()
conn.close()
print("Migration complete.")

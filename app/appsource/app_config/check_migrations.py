import sqlite3
import os

db_path = '../db.sqlite3'
if not os.path.exists(db_path):
    print("Database not found at %s" % db_path)
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("SELECT app, name FROM django_migrations")
    rows = cursor.fetchall()
    for row in rows:
        print("%s: %s" % (row[0], row[1]))
except Exception as e:
    print("Error: %s" % str(e))
finally:
    conn.close()

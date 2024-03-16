# CLI Script to view what is in the shorts (short urls) database.
import sqlite3

conn = sqlite3.connect('./../cache/shorts.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM short_urls") # Use WHERE clause with conditions to modify the result
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()

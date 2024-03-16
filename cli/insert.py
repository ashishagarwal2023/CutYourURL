# CLI Script to INSERT records in the shorts (short urls) database.
import sqlite3

conn = sqlite3.connect('./../cache/shorts.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO short_urls (short_url, original_url) VALUES (?, ?)") # Fill ? values too.
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
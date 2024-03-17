# CLI Script to DELETE records in the shorts (short urls) database.
import sqlite3

conn = sqlite3.connect('./../cache/shorts.db')
cursor = conn.cursor()

cursor.execute("DELETE ? FROM short_urls WHERE ID = ?") # Fill ? with a condition to filter
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()

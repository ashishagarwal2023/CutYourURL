# CLI Script to EDIT records in the shorts (short urls) database.
import sqlite3

conn = sqlite3.connect('./../cache/shorts.db')
cursor = conn.cursor()

cursor.execute("UPDATE short_urls SET original_url = ?, short_url = ? WHERE ID = ?") # Modify the ? values and change it according to your needs.
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
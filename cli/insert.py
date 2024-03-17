# CLI Script to INSERT records in the shorts (short urls) database.
import sqlite3

conn = sqlite3.connect('./../cache/shorts.db')
cursor = conn.cursor()

sql_insert = "INSERT INTO short_urls (short_url, original_url, views) VALUES (?, ?, 0)"

# Specify the values to be inserted
values = [("tEsTsH", "https://example.com"),
          ("anotherShort", "https://anotherexample.com")]

for value_set in values:
    cursor.execute(sql_insert, value_set)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
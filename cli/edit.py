# CLI Script to EDIT records in the shorts (short urls) database.
import sqlite3

conn = sqlite3.connect('./../cache/shorts.db')
cursor = conn.cursor()

sql_update = "UPDATE short_urls SET original_url = ?, short_url = ?, views = ? WHERE ID = ?"

# Specify the values to be updated
new_original_url = "https://newexample.com" # New URL
new_short_url = "newShort" # New short URL
new_views = 10  # Views to change to
record_id = 1  # Record ID to update

cursor.execute(sql_update, (new_original_url, new_short_url, new_views, record_id))

conn.commit()

conn.close()
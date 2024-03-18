import sqlite3

def recents(length=6):
    conn = sqlite3.connect('./cache/shorts.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT short_url, original_url, views, inserted_at FROM short_urls ORDER BY datetime(inserted_at) DESC LIMIT {length}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
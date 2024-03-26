import sqlite3
from datetime import datetime


def get_db():
    db = sqlite3.connect("cache/shorts.db")
    return db


def delete_expired_urls():
    now = datetime.now()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, expiryDate FROM short_urls")
    rows = cursor.fetchall()
    for row in rows:
        id, expiryDate = row
        print(f"Scaning...{id}")
        if expiryDate and datetime.strptime(expiryDate, "%Y-%m-%d %H:%M:%S.%f") < now:
            cursor.execute("DELETE FROM short_urls WHERE id=?", (id,))
            print(f"Deleted at {id}")
    db.commit()
    print(f"Scan done")


delete_expired_urls()

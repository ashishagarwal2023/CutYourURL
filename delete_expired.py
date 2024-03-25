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
        if expiryDate and datetime.strptime(expiryDate, "%Y-%m-%d %H:%M:%S.%f") < now:
            cursor.execute("DELETE FROM short_urls WHERE id=?", (id,))
    db.commit()


delete_expired_urls()

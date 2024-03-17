import sqlite3

DB_PATH = './../cache/shorts.db'

def getAllData():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM short_urls")
        rows = cursor.fetchall()
    return rows

def getQueryData(query):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM short_urls {query}")
        rows = cursor.fetchall()
    return rows

def insertData(short_url, original_url, views=0):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO short_urls (short_url, original_url, views) VALUES (?, ?, ?)", (short_url, original_url, views))
        conn.commit()

# Example usage with specified query
query_result = getQueryData("WHERE ID = 2")
print(query_result)

# Example usage of insertData

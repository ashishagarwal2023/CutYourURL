import os
import sys
import random
import string
import sqlite3
from flask import Flask, render_template, redirect, request, g, url_for
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import valid

black_shorts = ["new", "home", "website", "site", "about", "details", "contact"]
dir_name = "s"
DATABASE = './cache/shorts.db'
log_file_path = "./cache/logs/shorts.log"

app = Flask(__name__)

log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

if not os.path.exists(log_file_path):
    open(log_file_path, 'a').close()

log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d %b %Y at %H:%M:%S')
log_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=30)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.DEBUG)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(DATABASE)
        except sqlite3.OperationalError:
            print("Found no database, migtht be deleted. Restoring database!")
            os.execl(sys.executable, sys.executable, *sys.argv)
        db.execute('PRAGMA foreign_keys = ON')
    return db

def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def gen_short(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def shortUrl(url, length):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT short_url FROM short_urls WHERE original_url=?', (url))
    existing_short_url = cursor.fetchone()

    if existing_short_url:
        cursor.close()
        return f"{dir_name}/{existing_short_url[0]}"

    short_url = gen_short(length)
    while True:
        cursor.execute('SELECT * FROM short_urls WHERE short_url=?', (short_url,))
        existing_short_url = cursor.fetchone()
        if not existing_short_url:
            break
        short_url = gen_short(length)

    cursor.execute('INSERT INTO short_urls (short_url, original_url) VALUES (?, ?)', (short_url, url))
    db.commit()
    cursor.close()
    return f"{dir_name}/{short_url}"

@app.before_request
def before_request():
    if not getattr(g, '_got_first_request', None):
        init_db()
        g._got_first_request = True

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/short", methods=["POST", "GET"])
def short():
    if request.method == "POST":
        try:
            url = request.form.get("url")
            domain = request.url_root
            if valid.verify(url, domain):
                pass
            else:
                return render_template("generated.html", data=["err", ""])

            app.logger.info(f'POST request received for URL: {url}')

            short_url = shortUrl(url, 6)
            app.logger.info(f'Generated new short URL: /{short_url}\n')
            full = f"{request.url_root}{short_url}"
            return render_template("generated.html", data=[full, url])
        except Exception as e:
            return render_template("generated.html", data=["exc", e])
    else:
        return render_template("generated.html", data=["err", ""])

@app.route(f"/{dir_name}/<short_url>")
def redr_url(short_url):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT original_url, views FROM short_urls WHERE short_url=?', (short_url,))
    url_info = cursor.fetchone()

    if url_info:
        original_url, views = url_info
        views += 1
        cursor.execute('UPDATE short_urls SET views=? WHERE short_url=?', (views, short_url))
        db.commit()
        cursor.close()
        app.logger.info(f'Redirecting to original URL: {original_url}')
        return redirect(original_url)
    else:
        app.logger.warning('Short URL not found')
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

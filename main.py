# Coded by ashishagarwal2023
# Date initially published to GitHub: 17 March 2024 1AM
# DO NOT COPY!

import os
import random
import string
import sqlite3
from flask import Flask, render_template, redirect, request, g
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

log_file_path = "./cache/logs/shorts.log"
log_dir = os.path.dirname(log_file_path)

os.makedirs(log_dir, exist_ok=True)

if not os.path.exists(log_file_path):
    open(log_file_path, 'a').close()
    print(f"Created log file: {log_file_path}")
 

app = Flask(__name__)
DATABASE = './cache/shorts.db'
LOGS = './cache/logs/shorts.log'
print(f"Database at {DATABASE}, logging at {LOGS}")
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d %b %Y at %H:%M:%S')
log_handler = TimedRotatingFileHandler(LOGS, when='midnight', interval=1, backupCount=30)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.DEBUG)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute('PRAGMA foreign_keys = ON')
    return db


def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def gen_short(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.before_request
def before_request():
    if not getattr(g, '_got_first_request', None):
        init_db()
        g._got_first_request = True


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/shorts/new", methods=["POST", "GET"])
def short():
    if request.method == "POST":
        try:
            url = request.form.get("url")
            if not url.startswith("https://"):
                url = "https://" + url

            app.logger.info(f'POST request received for URL: {url}')

            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT short_url FROM short_urls WHERE original_url=?', (url,))
            existing_short_url = cursor.fetchone()

            if existing_short_url:
                cursor.close()
                app.logger.debug(f'Returning existing short URL: /shorts/{existing_short_url[0]}\n')
                return f"{request.url_root}{existing_short_url[0]}"

            short_url = gen_short()
            while True:
                cursor.execute('SELECT * FROM short_urls WHERE short_url=?', (short_url,))
                existing_short_url = cursor.fetchone()
                if not existing_short_url:
                    break
                short_url = gen_short()

            cursor.execute('INSERT INTO short_urls (short_url, original_url) VALUES (?, ?)', (short_url, url))
            db.commit()
            cursor.close()
            app.logger.info(f'Generated new short URL: /shorts/{short_url}\n')
            return f"{request.url_root}shorts/{short_url}"
        except:
            return "Not a valid POST response", 400    
    else:
        return render_template("generated.html")


black_shorts = ["new", "home", "website", "site", "about", "details", "contact"]

@app.route("/shorts/<short_url>")
def redr_url(short_url):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT original_url FROM short_urls WHERE short_url=?', (short_url,))
    url = cursor.fetchone()
    cursor.close()

    if url:
        app.logger.info(f'Redirecting to original URL: {url[0]}')
        return redirect(url[0])
    else:
        app.logger.warning('Short URL not found')
        return "Not found", 404


if __name__ == "__main__":
    app.run(debug=True)

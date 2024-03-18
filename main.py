import os
import sys
import random
import string
import sqlite3
import flask
from flask import Flask, render_template, redirect, request, g, url_for
import logging
from logging.handlers import TimedRotatingFileHandler
import valid
import flask_login as fl
import recent
login_manager = fl.LoginManager()

LOGIN_DB = "./cache/login.db"
black_shorts = ["new", "home", "website", "site", "about", "details", "contact"]
dir_name = "s"
DATABASE = './cache/shorts.db'
log_file_path = "./cache/logs/shorts.log"
SCHEMA_FILE = "./login.sql"

with sqlite3.connect(LOGIN_DB) as db:
    cursor = db.cursor()
    q = "SELECT * FROM users"
    cursor.execute(q, ())
    users = cursor.fetchall()
    
app = Flask(__name__)
login_manager.init_app(app)
app.secret_key = 'tBwMEtArOWakISWGAfJzDJL8IPzMu9j0' 

class User(fl.UserMixin):
    def __init__(self, username):
        db = sqlite3.connect(LOGIN_DB)
        cursor = db.cursor()
        q = "SELECT * FROM users WHERE username = ?"
        user = cursor.execute(q, (username,)).fetchone()
        self.id = username
    

@login_manager.user_loader
def user_loader(username):
    return User(username)

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username
    return user

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
    cursor.execute('SELECT short_url FROM short_urls WHERE original_url=?', (url,))
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

    cursor.execute('INSERT INTO short_urls (short_url, original_url) VALUES (?, ?)', (short_url, url,))
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
    if fl.current_user.is_authenticated:
        username = fl.current_user.id
    else:
        username = ""

    return render_template("index.html", username=username, recents=recent.recents(6))

@app.route("/short", methods=["POST", "GET"])
def short():
    if request.method == "POST":
        try:
            url = request.form.get("url")
            domain = request.url_root
            if valid.verify(url, domain):
                pass #Valid
            else:
                # Invalid
                return render_template("generated.html", data=["err", "", 0])
            db = get_db()
            Vcursor = db.cursor()
            Vcursor.execute('SELECT views FROM short_urls WHERE original_url=?', (url,))
            views = Vcursor.fetchone()

            app.logger.info(f'POST request received for URL: {url}')

            short_url = shortUrl(url, 6)
            app.logger.info(f'Generated new short URL: /{short_url}\n')
            full = f"{request.url_root}{short_url}"
            views = views[0] if views else 0
            # New
            return render_template("generated.html", data=[full, url, views])
        except Exception as e:
            return render_template("generated.html", data=["exc", e]) # Server error
    else:
        return render_template("generated.html", data=["err", ""]) # GET without parameters or smh

@app.route(f"/{dir_name}/<short_url>")
def redr_url(short_url):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT original_url, views FROM short_urls WHERE short_url=?', (short_url,))
    url_info = cursor.fetchone()

    if url_info:
        original_url, views = url_info
        views += 1
        cursor.execute('UPDATE short_urls SET views=? WHERE short_url=?', (views, short_url,))
        db.commit()
        cursor.close()
        app.logger.info(f'Redirecting to original URL: {original_url}')
        return redirect(original_url)
    else:
        app.logger.warning('Short URL not found')
        return redirect(url_for("index"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html', data="null")

    username = flask.request.form['username']
    password = flask.request.form['password']

    db = sqlite3.connect(LOGIN_DB)
    cursor = db.cursor()
    cursor.execute('SELECT password FROM users WHERE username=?', (username,))
    result = cursor.fetchone()

    if result and password == result[0]:
        user = User(username)
        user.id = username
        fl.login_user(user)
        return flask.redirect(flask.url_for('index'))

    return render_template("login.html", data=0) # when there is not valid username/password
# try out on the web server yourself, you cannot login with invalid creds

@app.route('/signup', methods=['POST'])
def signup():
    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']
    confirm_password = flask.request.form['confirmPassword']

    if password != confirm_password:
        return render_template("login.html", data=1)

    db = sqlite3.connect(LOGIN_DB)
    cursor = db.cursor()
    
    # Check if the username already exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE username=?', (username,))
    count = cursor.fetchone()[0]
    if count > 0:
        return render_template("login.html", data=2)

    # Insert the new user record
    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    db.commit()

    return flask.redirect(flask.url_for('login'))


@app.route('/logout')
def logout():
    fl.logout_user()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

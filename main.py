# Imports
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
from qr import qr

login_manager = fl.LoginManager()

# Variables, should be modified to your needs!
LOGIN_DB = "./cache/login.db"
black_shorts = ["new", "home", "website", "site", "about", "details", "contact"] # Not implemented yet
dir_name = "s"
DATABASE = './cache/shorts.db'
log_file_path = "./cache/logs/shorts.log"
SCHEMA_FILE = "./login.sql"

# Load DB
with sqlite3.connect(LOGIN_DB) as db:
    cursor = db.cursor()
    q = "SELECT * FROM users"
    cursor.execute(q, ())
    users = cursor.fetchall()

app = Flask(__name__)
login_manager.init_app(app)
app.secret_key = 'tBwMEtArOWakISWGAfJzDJL8IPzMu9j0' # Change this if you want!

def cutText(text, length):
    if len(text) <= length:
        return text
    else:
        return text[:(length-3)] + "..."


# User class
class User(fl.UserMixin):
    def __init__(self, username):
        db = sqlite3.connect(LOGIN_DB)
        cursor = db.cursor()
        q = "SELECT * FROM users WHERE username = ?"
        user = cursor.execute(q, (username,)).fetchone()
        self.id = username


# Flask_login related tasks for Login/Signup
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

# Make dir for logs if it does not exist
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

# Make log file
if not os.path.exists(log_file_path):
    open(log_file_path, 'a').close()

# Initialize logging
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d %b %Y at %H:%M:%S')
log_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=30)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.DEBUG)

# Restore the shorts.db database if it was deleted
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

# Close DB function
def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# To make shorts db from schema
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# Random ID Generator Method
def gen_short(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


# After a short URL id is made, this function holds the further tasks
# Like to add the URL to database, check if it already exists.
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

# Init db to make sure it exists (only for shorts.db)
@app.before_request
def before_request():
    if not getattr(g, '_got_first_request', None):
        init_db()
        g._got_first_request = True

# Homepage
@app.route("/", methods=["GET", "POST"])
def index():
    if fl.current_user.is_authenticated:
        username = fl.current_user.id
    else:
        username = "" # Guest username, is trimmed on client-side

    return render_template("index.html", username=username, recents=recent.recents(5), cutText=cutText) # Recent shorts are supplied and username is too

@app.route("/short", methods=["POST", "GET"]) # Route where links are shorted
def short():
    if request.method == "POST":
        try:
            url = request.form.get("url")
            domain = request.url_root
            if valid.verify(url, domain):
                pass # The given URL is valid, we can continue to shorten it
            else:
                # The given URL is not valid, we can not continue with such a URL.
                return render_template("generated.html", data=["err", "", 0],cutText=cutText)
            db = get_db()
            Vcursor = db.cursor()
            Vcursor.execute('SELECT views FROM short_urls WHERE original_url=?', (url,))
            views = Vcursor.fetchone() # Gets the views of the URL, it will be None if its new generated, giving the idea of whether it is generated or existing.

            app.logger.info(f'POST request received for URL: {url}')

            short_url = shortUrl(url, 6)
            if views == None: # None means its just generated
                app.logger.info(f'Generated new short URL: /{short_url}\n')
            else: # Already existed
                app.logger.info(f'Returning already-generated URL: /{short_url}\n')
            full = f"{request.url_root}{short_url}" # Generates a URL like http://127.0.0.1:5000/s/4n8MSl
            views = views[0] if views else 0
            qrURI = qr(full)
            app.logger.info(f'Generated QR Code URI from: {full}\n')
            return render_template("generated.html", data=[full, url, views, qrURI],cutText=cutText) # Success
        except Exception as e:
            app.logger.error(f'Server exception during shorting: {e}\n')
            return render_template("generated.html", data=["exc", e]) # Server exception
    else:
        app.logger.error(f'GET request received without parameters for /short\n')
        return render_template("generated.html", data=["err", ""]) # GET without parameters, client error.

@app.route(f"/{dir_name}/<short_url>") # Route where short URLs are redirected to their original URLs
def redr_url(short_url):
    app.logger.info(f'Recieved to redirect for short with ID: {short_url}\n')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT original_url, views FROM short_urls WHERE short_url=?', (short_url,))
    # Gets the original URL and views
    url_info = cursor.fetchone()

    if url_info:
        original_url, views = url_info
        views += 1 # Increase view count by 1
        cursor.execute('UPDATE short_urls SET views=? WHERE short_url=?', (views, short_url,))
        # Updates the view count
        db.commit()
        cursor.close()
        app.logger.info(f'Redirecting to original URL: {original_url}')
        return redirect(original_url) # Redirects
    else:
        app.logger.error('Short URL not found')
        return redirect("/") # If the Short URL doesn't exist, we will simply redirect to the homepage.

# The login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET' and not fl.current_user.is_authenticated:
        return render_template('login.html', data="null")
    # GET requests are when someone comes there without any data, like opened from address bar or bookmark or jumped
    if not fl.current_user.is_authenticated:
        username = flask.request.form['username']
        password = flask.request.form['password']

        db = sqlite3.connect(LOGIN_DB)
        cursor = db.cursor()
        cursor.execute('SELECT password FROM users WHERE username=?', (username,))
        result = cursor.fetchone()

        if result and password == result[0]: # Result is the valid (actual, stored) password and password is the form's password
            # If both are same, then we can login, because your password = correct password
            user = User(username)
            user.id = username
            fl.login_user(user)
            return flask.redirect("/") # Redirect to home after being logged in

        return render_template("login.html", data=0) # The password or username is invalid.
    return redirect("/") # The user is already logged in

@app.route('/signup', methods=['GET','POST']) # Signup route
def signup():
    if flask.request.method == 'POST' and not fl.current_user.is_authenticated:
        username = flask.request.form['username']
        email = flask.request.form['email']
        password = flask.request.form['password']
        confirm_password = flask.request.form['confirmPassword']

        if password != confirm_password: # Passwords are not equal
            return render_template("login.html", data=1) # Client Error : Passwords do not match

        db = sqlite3.connect(LOGIN_DB)
        cursor = db.cursor()

        # Check if the username already exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username=?', (username,))
        count = cursor.fetchone()[0]
        if count > 0:
            return render_template("login.html", data=2) # Client Error : Username taken

        # Insert the new user record
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password)) # Signed up
        user = User(username)
        user.id = username
        fl.login_user(user) # Login
        db.commit() # The account has been created and logged in now.

        return flask.redirect("/") # Successfully signed up!
    else:
        return flask.redirect("/") # They are already logged in, or they are calling GET
    # Must logout to signup/login


# Logout account, if logged in. Nothing happens to guests.
@app.route('/logout')
def logout():
    if fl.current_user.is_authenticated:
        fl.logout_user()
    return redirect("/") # To the homepage

# The 404 page
@app.errorhandler(404)
def page_not_found(e):
    return redirect("/") # 404 to homepage

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))

import logging
import os
import random
import sqlite3
import string
import threading
import time
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

import flask
import flask_login as fl
import schedule
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    g,
    jsonify,
)

import otp as o
import valid
from delete_expired import delete_expired_urls
from qr import qr

load_dotenv()

login_manager = fl.LoginManager()

# Variables, should be modified to your needs!
black_shorts = [
    # back again
    "new",
    "home",
    "website",
    "site",
    "about",
    "elepha",
    "details",
    "contact",
]
LOGIN_DB = os.getenv("LOGIN_DB")
dir_name = os.getenv("dir_name")
DATABASE = os.getenv("DATABASE")
log_file_path = os.getenv("log_file_path")
SCHEMA_FILE = os.getenv("SCHEMA_FILE")
captchaSiteKey = os.getenv("captchaSiteKey")
spoofDomain = os.getenv("spoofDomain")
secretKey = os.getenv("secretKey")


def job():
    delete_expired_urls()


schedule.every(1).days.do(job)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
scheduler_thread.start()


def recents(length=6):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT short_url, original_url, views, inserted_at FROM short_urls WHERE public = 1 ORDER BY datetime("
        f"inserted_at) DESC LIMIT {length}"
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def getTime(add):
    now = datetime.now()
    return now + timedelta(days=add)


def get_login():
    logindb = sqlite3.connect(LOGIN_DB)
    return logindb


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(DATABASE)
        except sqlite3.OperationalError:
            print("Found no database, migtht be deleted. Restoring database!")
            os.execl(sys.executable, sys.executable, *sys.argv)
        db.execute("PRAGMA foreign_keys = ON")
    return db


# Close DB function
def close_db(exception=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# To make shorts db from schema
def init_db():
    db = get_db()
    with app.open_resource("schema.sql", mode="r") as f:
        db.cursor().executescript(f.read())
        print("loaded")
    db.commit()


app = Flask(__name__)
login_manager.init_app(app)
app.secret_key = secretKey

# Load DB
with sqlite3.connect(LOGIN_DB) as db:
    cursor = db.cursor()
    q = "SELECT * FROM users"
    cursor.execute(q, ())
    users = cursor.fetchall()


def cutText(text, length):
    if len(text) <= length:
        return text
    else:
        return text[: (length - 3)] + "..."


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
    username = request.form.get("username")
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
    open(log_file_path, "a").close()

# Initialize logging
log_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%d %b %Y at %H:%M:%S"
)
log_handler = TimedRotatingFileHandler(
    log_file_path, when="midnight", interval=1, backupCount=30
)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.DEBUG)


# Random ID Generator Method
def gen_short(length=6):
    chars = string.ascii_letters + string.digits
    short_id = "".join(random.choice(chars) for _ in range(length))
    while short_id in black_shorts:
        short_id = "".join(random.choice(chars) for _ in range(length))
    return short_id


def verify_otp_for_user(username, otp):
    logindb = get_login()
    cursorlogin = logindb.cursor()
    cursorlogin.execute("SELECT OTP FROM users WHERE username=?", (username,))
    result = int(cursorlogin.fetchone()[0])
    otp = int(otp)

    if otp == result:
        cursorlogin.execute("UPDATE users SET verified=1 WHERE username=?", (username,))
        logindb.commit()
        cursorlogin.close()
        return True
    else:
        return False


# After a short URL id is made, this function holds the further tasks
# Like to add the URL to database, check if it already exists.
def shortUrl(url, length, captcha, visb, expiryDate):
    db = get_db()
    expiryClicks = int(request.form.get("expiryClicks"))
    if not float(expiryDate) == 0:
        expiryDate = getTime(float(expiryDate))
    else:
        expiryDate = 0
    visb = 1 if visb == "on" else 0
    cursor = db.cursor()
    cursor.execute("SELECT short_url FROM short_urls WHERE original_url=?", (url,))
    existing_short_url = cursor.fetchone()

    if existing_short_url:
        cursor.close()
        return f"{dir_name}/{existing_short_url[0]}"

    # Retrieve the custom slug value from the form data
    customSlug = request.form.get("slugInput")
    # Replace all 'X' in the customSlug with a random character
    for _ in range(customSlug.count("X")):
        customSlug = customSlug.replace("X", gen_short(1), 1)

    # Check if custom slug is provided and not already in use
    if customSlug and not customSlug.isspace():
        cursor.execute("SELECT * FROM short_urls WHERE short_url=?", (customSlug,))
        existing_short_url = cursor.fetchone()
        if not existing_short_url:
            short_url = customSlug
        else:
            short_url = gen_short(length)
    else:
        short_url = gen_short(length)

    # Only generate a new short_url if a custom slug was not provided or was already in use
    short_url = customSlug
    if not customSlug or existing_short_url:
        while True:
            cursor.execute("SELECT * FROM short_urls WHERE short_url=?", (short_url,))
            existing_short_url = cursor.fetchone()
            if not existing_short_url:
                break
            short_url = gen_short(length)

    captcha_enabled = False
    if int(captcha) == 1:
        captcha_enabled = True

    cursor.execute(
        "INSERT INTO short_urls (short_url, original_url, captcha, public, expiryClicks, expiryDate) VALUES (?, ?, ?, "
        "?, ?, ?)",
        (short_url, url, captcha_enabled, visb, expiryClicks, expiryDate),
    )
    db.commit()
    cursor.close()
    return f"{dir_name}/{short_url}"


# Init db to make sure it exists (only for shorts.db)
@app.before_request
def before_request():
    if not getattr(g, "_got_first_request", None):
        init_db()
        g._got_first_request = True


# Homepage
@app.route("/", methods=["GET", "POST"])
def index():
    logindb = get_login()
    cursorlogin = logindb.cursor()
    verified = True
    if fl.current_user.is_authenticated:
        username = fl.current_user.id
        result = cursorlogin.execute(
            "SELECT verified FROM users WHERE username=?", (username,)
        ).fetchone()
        if result:
            verified = result[0]
        else:
            verified = True
    else:
        username = ""  # Guest username, is trimmed on client-side

    return render_template(
        "index.html",
        username=username,
        recents=recents(5),
        cutText=cutText,
        verified=verified,
    )  # Recent shorts are supplied and username is too


@app.route("/short", methods=["POST", "GET"])  # Route where links are shorted
def short():
    username = ""
    if fl.current_user.is_authenticated:
        username = fl.current_user.id
    if request.method == "POST":
        try:
            url = request.form.get("url")
            expiryDate = float(request.form.get("expiryDate"))
            isPublic = request.form.get("public")
            captchaEnabled = "captcha" in request.form
            logindb = get_login()
            cursorlogin = logindb.cursor()
            verified = True
            if fl.current_user.is_authenticated:
                verified = cursorlogin.execute(
                    "SELECT verified FROM users WHERE username=?", (username,)
                ).fetchone()[0]

            if valid.verify(url):
                pass  # The given URL is valid, we can continue to shorten it
            else:
                # The given URL is not valid, we can not continue with such a URL.
                return render_template(
                    "generated.html",
                    data=["err", ""],
                    username=username,
                    verified=verified,
                )
            db = get_db()
            Vcursor = db.cursor()
            Vcursor.execute("SELECT views FROM short_urls WHERE original_url=?", (url,))
            views = (
                Vcursor.fetchone()
            )  # Gets the views of the URL, it will be None if its new generated, giving the idea of whether it is generated or existing.

            app.logger.info(f"POST request received for URL: {url}")

            short_url = shortUrl(
                url, 6, captcha=captchaEnabled, visb=isPublic, expiryDate=expiryDate
            )
            if views == None:  # None means its just generated
                app.logger.info(f"Generated new short URL: /{short_url}\n")
            else:  # Already existed
                app.logger.info(f"Returning already-generated URL: /{short_url}\n")
            full = f"{spoofDomain}{short_url}"  # Generates a URL like http://127.0.0.1:5000/s/4n8MSl
            views = views[0] if views else 0
            qrURI = qr(full)
            app.logger.info(f"Generated QR Code URI from: {full}\n")
            croppedURL = cutText(url, 30)
            return render_template(
                "generated.html",
                full=full,
                url=url,
                views=views,
                qrURI=qrURI,
                username=username,
                captchaEnabled=captchaEnabled,
                cropped=croppedURL,
                verified=verified,
            )  # Success
        except Exception as e:
            app.logger.error(f"Server exception during shorting: {e}\n")
            print(e)
            return render_template(
                "generated.html",
                data=["exc"],
                username=username,
                cropped="",
                verified=verified,
            )  # Server exception
    else:
        app.logger.error(f"GET request received without parameters for /short\n")
        return redirect("/")  # GET without parameters, client error.


@app.route(f"/{dir_name}/<short_url>")
def redr_url(short_url):
    app.logger.info(f"Recieved to redirect for short with ID: {short_url}\n")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT original_url, captcha, views, expiryClicks FROM short_urls WHERE short_url=?",
        (short_url,),
    )
    url_info = cursor.fetchone()

    if url_info:
        original_url, captcha, views, expiryClicks = url_info
        if captcha:
            app.logger.info(f"Redirecting to captcha page for short URL: {short_url}")
            return render_template(
                "captcha.html",
                redirectURL=original_url,
                captchaKey=captchaSiteKey,
                short_id=short_url,
            )
        views += 1
        if (
            views >= expiryClicks and expiryClicks != 0
        ):  # Check if the expiry clicks limit has been reached
            cursor.execute(
                "DELETE FROM short_urls WHERE short_url=?",
                (short_url,),
            )
        else:
            cursor.execute(
                "UPDATE short_urls SET views=? WHERE short_url=?",
                (
                    views,
                    short_url,
                ),
            )
        db.commit()
        cursor.close()
        app.logger.info(f"Redirecting to original URL: {original_url}")
        return redirect(original_url)
    else:
        app.logger.error("Short URL not found")
        return redirect("/")


# The login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET" and not fl.current_user.is_authenticated:
        return render_template("login.html", error="null")
    # GET requests are when someone comes there without any data, like opened from address bar or bookmark or jumped
    if not fl.current_user.is_authenticated:
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        db = sqlite3.connect(LOGIN_DB)
        cursor = db.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if (
            result and password == result[0]
        ):  # Result is the valid (actual, stored) password and password is the form's password
            # If both are same, then we can login, because your password = correct password
            user = User(username)
            user.id = username
            fl.login_user(user)
            return flask.redirect("/")  # Redirect to home after being logged in

        return render_template(
            "login.html", error=0
        )  # The password or username is invalid.
    return redirect("/")  # The user is already logged in


@app.route("/signup", methods=["GET", "POST"])  # Signup route
def signup():
    if flask.request.method == "POST" and not fl.current_user.is_authenticated:
        username = flask.request.form["username"]
        email = flask.request.form["email"]
        password = flask.request.form["password"]
        confirm_password = flask.request.form["confirmPassword"]

        if password != confirm_password:  # Passwords are not equal
            return render_template(
                "login.html", error=1
            )  # Client Error : Passwords do not match

        db = sqlite3.connect(LOGIN_DB)
        cursor = db.cursor()

        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username=?", (username,))
        count = cursor.fetchone()[0]
        if count > 0:
            return render_template(
                "login.html", error=2
            )  # Client Error : Username taken

        otp = o.otp(username, email)
        if not otp:
            return render_template("login.html", error=3)

        # Insert the new user record
        cursor.execute(
            "INSERT INTO users (username, email, password, OTP) VALUES (?, ?, ?, ?)",
            (username, email, password, otp),
        )  # Signed up
        user = User(username)
        user.id = username
        fl.login_user(user)  # Login
        db.commit()  # The account has been created and logged in now.

        return flask.redirect("/")  # Successfully signed up!
    else:
        return flask.redirect(
            "/"
        )  # They are already logged in, or they are calling GET
    # Must logout to signup/login


# Logout account, if logged in. Nothing happens to guests.
@app.route("/logout")
def logout():
    if fl.current_user.is_authenticated:
        fl.logout_user()
    return redirect("/")  # To the homepage


# The 404 page
@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")  # 404 to homepage


@app.route("/captcha", methods=["POST"])
def captcha():
    short_url = flask.request.form["short_url"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT original_url, views FROM short_urls WHERE short_url=?",
        (short_url,),
    )
    url_info = cursor.fetchone()

    if url_info:
        original_url, views = url_info
        views += 1
        cursor.execute(
            "UPDATE short_urls SET views=? WHERE short_url=?",
            (
                views,
                short_url,
            ),
        )
        db.commit()
        cursor.close()
        return original_url
    else:
        return redirect("/")


@app.route("/account")
def account():
    logindb = get_login()
    cursorlogin = logindb.cursor()
    if fl.current_user.is_authenticated:
        username = fl.current_user.id
        verified = cursorlogin.execute(
            "SELECT verified, email FROM users WHERE username=?", (username,)
        ).fetchone()
        email = verified[1]
        verified = verified[0]
        if verified == 1:
            verified = True
        else:
            verified = False
    else:
        username = ""
        return redirect("/login")
    return render_template(
        "account.html", email=email, username=username, verified=verified
    )


@app.route("/account/verifyOtp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    otp = data.get("otp")
    username = data.get("username")
    is_valid = verify_otp_for_user(username, otp)
    return jsonify(is_valid)


@app.route("/account/changeEmail", methods=["POST"])
def change_email():
    data = request.get_json()
    new_email = data.get("email")
    username = data.get("username")
    logindb = get_login()
    cursorlogin = logindb.cursor()
    cursorlogin.execute(
        "UPDATE users SET email=?, verified = 0 WHERE username=?", (new_email, username)
    )
    logindb.commit()
    cursorlogin.close()
    resend_otp()
    return jsonify(True)


@app.route("/account/resendOTP", methods=["POST"])
def resend_otp():
    data = request.get_json()
    username = data.get("username")
    logindb = get_login()
    cursorlogin = logindb.cursor()
    cursorlogin.execute("SELECT email FROM users WHERE username=?", (username,))
    email = cursorlogin.fetchone()[0]
    otp = o.otp(username, email)
    cursorlogin.execute("UPDATE users SET OTP=? WHERE username=?", (otp, username))
    logindb.commit()
    cursorlogin.close()
    return jsonify(True)


@app.route("/account/changePassword", methods=["POST"])
def change_password():
    data = request.get_json()
    new_pass = data.get("new_pass")
    current_pass = data.get("current_pass")
    username = data.get("username")
    confirm_pass = data.get("confirm_pass")
    logindb = get_login()
    cursorlogin = logindb.cursor()
    cursorlogin.execute("SELECT password FROM users WHERE username=?", (username,))
    password = cursorlogin.fetchone()[0]
    if password == current_pass:
        if new_pass == confirm_pass and (not (current_pass == new_pass)):
            cursorlogin.execute(
                "UPDATE users SET password=? WHERE username=?", (new_pass, username)
            )
            logindb.commit()
            cursorlogin.close()
            return jsonify(True)
        else:
            return jsonify(False)
    else:
        return jsonify(False)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))

<p align="center">
  <a href="https://cutyoururl.pythonanywhere.com" rel="noopener">
 <img width=200px height=200px src="static/CutYourURL.png" alt="CutYourURL Logo"></a>
</p>
<h3 align="center">CutYourURL</h3>
<p align="center"> 🤖 Shorten your links for free with a powerful interface!
    <br>
</p>
<div align="center">

[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dashish_agarwal%26type%3Dpledges&style=flat)](https://patreon.com/ashish_agarwal)

[Try out here! ⤴](https://cutyoururl.pythonanywhere.com)

</div>

## 📝 Table of Contents

- [About](#about)
- [Demo / Working](#demo)
- [How it works](#working)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

I built this project to make a free URL shortener with a powerful interface. It is based on Python-Flask and SQLite3. It is a free and open-source project, and you can use it for free. It is hosted on PythonAnywhere, and you can try it out [here](https://cutyoururl.pythonanywhere.com).

It's not simple as writting a script. For this, I used some other libraries like to generate QR codes, flask-login for authentication and SQL. And it is also integrated with Gmail API, so it can verify emails.

> Consider helping me and not making a spambot for my site, I cannot invest a bit on it. Try to support me, if you can!

## 🎥 Demo / Working <a name = "demo"></a>

Demo will be available soon.

## 💭 How it works <a name = "working"></a>

You enter a long URL and we'll save it and give you a short URL. You can get a free QR code for your URL too, views counting, and automatically delete the URL when it reaches a amount of clicks or a date (limited clicks or expiry date). You can also have custom slugs on your URLs!

## Running locally
### Prerequisites

Start a new virtual environment and install all requirements

```bash
$ python3 -m pip install -r requirements.txt
```
### Making .env
Then, you need to make a `.env` file in the project's root directory with the following content:
```env
LOGIN_DB=./cache/login.db
dir_name=s
DATABASE=./cache/shorts.db
log_file_path=./cache/logs/shorts.log
SCHEMA_FILE=./login.sql
captchaSiteKey=dont try me
spoofDomain=http://127.0.0.1:5000/
secretKey=somethingbruh
```
> - Login DB: path to login db file
> - Dir Name: route for generated shorts like /short/shortIDHERE, where short is the dir
> - Database: path to shorts db file
> - Log File Path: path to log file
> - Schema File: path to schema file for login db
> - Captcha Site Key: Google Captcha Site Key (v2 Site Key)
> - Spoof Domain: The domain to spoof, like to show the paths at this domain (for example, https://cutyoururl.tech/ would be the spoof domain for the path https://cutyoururl.tech/short/shortIDHERE)
> - The secret key: used for server and browser to talk. If it is leaked, consider changing it to prevent peoples from abusing it. A certificate that says a user valid.

You can get the captcha site key from [here](https://www.google.com/recaptcha/admin/create)

### Adding Gmail Services
You need to add a `credentials.json` file in the project's root directory. You can get it from [here](https://developers.google.com/gmail/api/quickstart/python). You can also use the `token.pickle` file to store the token, but it is not necessary.

> Do not leak your `token.pickle` file, it can allow someone to take over your account.

### Logging in
After you got your credentials, you can run the following command which will attempt to send a simple email. Gmail API will automatically ask you to login.

```bash
$ python3 test.py
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth

# Authorize it
# If you get a error Invalid TO Header, then you are done
```

## Common Errors
### Cannot Access DB
This error will occur if Python cannot open the DB under `./cache/login.db`. If you deleted the cache folder, it is not a issue, you can re-make it.
> In the few next updates I'll be trying to automatically make the shorts and login db from schema, however errors comes everywhere.

To re-make the login.db, you have to do:
```bash
$ sqlite3 login.db < login.sql # the login.db would be made
$ sqlite3 shorts.db < schema.sql # the shorts.db would be made

# move both to cache folder
$ mv ./login.db ./cache/
$ mv ./shorts.db ./cache/
```

Make sure you have installed all dependencies too!

## ✍️ Authors <a name = "authors"></a>

- [@ashishagarwal2023](https://github.com/ashishagarwal2023) - Idea & Initial work
- [@N3RDIUM](https://github.com/N3RDIUM) - Leaving me at the half back-end of login 🤣

See also the list of [contributors](https://github.com/ashishagarwal2023/cutyoururl/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Hat tip to anyone whose code was used
- Inspiration
- References

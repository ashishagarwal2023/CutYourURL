<p align="center">
  <a href="https://cutyoururl.tech/" rel="noopener">
 <img width=200px height=200px src="static/CutYourURL.png" alt="CutYourURL Logo"></a>
</p>
<h3 align="center">CutYourURL.tech</h3>
<p align="center"> 🤖 Shorten your links for free with a powerful interface!
    <br>
</p>
<div align="center">

[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dashish_agarwal%26type%3Dpledges&style=flat)](https://patreon.com/ashish_agarwal)

[Try out here! ⤴](https://cutyoururl.tech/)

</div>

## 📝 Table of Contents

- [About](#about)
- [Demo / Working](#demo)
- [How it works](#working)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

I just wanted to have a cool project, and I made this. I also need to shorten some URLs, and bit.ly's URL shortner is good but not free and it requires me to have a account.

Just a project to include in my stack. Also, this domain is just a 1-year domain from GitHub Student Dev Pack, I'm not sure where would I move it after it expires.

> For information about every commits (not all, but new feature ones), there is a updates.md file.

> Consider helping me and not making a spambot for my site, I cannot invest a bit on it. Try to support me, if you can!

## 🎥 Demo / Working <a name = "demo"></a>

Demo will be available soon.

## 💭 How it works <a name = "working"></a>

Based on Python-Flask. It saves your shortened URLs to a database and keeps logging infos too. This makes it much easier and faster to have a API!

## Running locally
### Prerequisites

Make venv yourself, then install the packages.

```bash
python3 -m pip install -r requirements.txt
```

### Running

```bash
python3 main.py

# Gunicorn is also installed with the requirements (needed to host on server)
# You can use gunicorn for local server too!
# Gunicorn will be installed from requirements
python3 -m gunicorn main:app
```

## Common Errors
It should not do any errors, and to prevent errors by the versions of new packages, I've specificed my version of all packages I'm using that is stable. However, theres still some errors:
### Cannot Access DB
This error will occur if Python cannot open the DB under `./cache/login.db`. If you deleted the cache folder, it is not a issue, you can re-make it.
> It will try to make ./cache/shorts.db automatically, but after running it and having login.db you don't have shorts.db, you might manually create one.

To re-make the login.db, you have to do:
```bash
# sudo apt install sqlite3
$ sqlite3 login.db < login.sql # install if not installed from apt

# then move login.db to cache
$ mv ./login.db ./cache/

# a login

# if u need to restore the shorts.db, similiarly:
$ sqlite3 shorts.db < schema.sql
$ mv ./shorts.db ./cache/

# Similiar tasks to make login.db and so for shorts.db
```
> As of the last yesterday's update, I tried to automatically make the both databases whenever they are needed, but not guranteed. Few users might face a site down when the database is generating (very rare)

Make sure you have installed all dependencies too!

## ✍️ Authors <a name = "authors"></a>

- [@ashishagarwal2023](https://github.com/ashishagarwal2023) - Idea & Initial work
- [@N3RDIUM](https://github.com/N3RDIUM) - Leaving me at the half back-end of login 🤣

See also the list of [contributors](https://github.com/ashishagarwal2023/cutyoururl/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Hat tip to anyone whose code was used
- Inspiration
- References

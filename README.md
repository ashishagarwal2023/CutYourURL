<p align="center">
  <a href="https://ashish2023.pythonanywhere.com/" rel="noopener">
 <img width=200px height=200px src="static/CutYourURL.png" alt="CutYourURL Logo"></a>
</p>

<h3 align="center">CutYourURL.me</h3>
<p align="center"> 🤖 Shorten your links for free with a powerful interface!
    <br> 
</p>
<div align="center">

[![Support me on Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dashish_agarwal%26type%3Dpledges&style=flat)](https://patreon.com/ashish_agarwal)

</div>

## 📝 Table of Contents

- [About](#about)
- [Demo / Working](#demo)
- [How it works](#working)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

I just wanted to have a cool project, and I made this. I also need to shorten some URLs, and bit.ly's URL shortner is good but not free and it requires me to have a account.

For being lazy to login, I just made this. 🧐

Just a party to include in my full-stack list. Also, this domain is just a 1-year domain from GitHub Student Dev Pack, I'm not sure where would I move it after it expires.

## 🎥 Demo / Working <a name = "demo"></a>

Demo will be available soon.

## 💭 How it works <a name = "working"></a>

Based on Python-Flask. It saves your shortened URLs to a database and keeps logging infos too. This makes it much easier and faster to have a API!

> I'm planning to make seperate mirrors, so that every day, to optimize the database, every mirror be different and new shorts directly go to the newest mirror (each mirror having 100 shorts, then a new mirror and so on). It would help me fix the population issue before deployments. 💀

## Running locally
### Prerequisites

Make venv yourself, then install the packages.

```bash
python3 -m pip install -r requirements.txt
```

### Running

```bash
python3 main.py
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

# if u need to restore the shorts.db, similiarly:
$ sqlite3 shorts.db < schema.sql
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

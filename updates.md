# 18 March 2024:
## What is added
Today were like 8+ commits done, these features were added:
- Template for user (when they are logged in or are guest, shows always on / route)
- Template for recent shorts (on / route)

## New files
Extra files added too:
- login-backup-empty.db: the backup of the login.db file initialized with the table without any data
- shorts-backup-empty: the backup of login.db file initialized with the table without any data

(And some more files related to templates)

## More:
- Added some more comments in the code
- Added some more info in the readme file
- Info about new changes will now be added on every day's commits
<details><summary>Bug fix: recent shorts is empty table when there is no data in the shorts db</summary>Now it will show you that there is no data.</details>
<details><summary>Bug fix: able to login or signup even already logged in</summary>You cannot do that anymore now, you will be redirected to / route</details>
<details><summary>Bug fix: logout always tries to logout even not logged in</summary>You will be logged out to / route if you were logged in, and always redirected to home.</details>
<details><summary>Feature: signup should instantly login with the signed-up account</summary>Ok, this is now added.</summary>
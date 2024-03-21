# 21 March 2024:

## News

- [cutyoururl.tech](https://cutyoururl.tech) is now properly working
- The connection is now secure and served on HTTPS

I'm working to resolve the issue where the connection is not secure, might be done tommorow.

## Modifications

We've got a updatte!

<details>
<summary>Added /accounts route</summary>

- You can verify your email there
- Change your email
- Change your password

If your account is not verified, /short and homepage routes will show you a banner "Your account is not verified, please verify your email to continue."
</details>

Files modified:
- Added /templates/account/change.html
- Added /templates/account/verify.html
- Added /templates/widgets/status.html
- Modified /templates/widgets/user.html
- Renamed /templates/comps to /templates/widgets

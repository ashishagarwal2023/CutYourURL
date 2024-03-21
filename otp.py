import base64
import os.path
import pickle
import random
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def email(to, subject, body):
	creds = None
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('gmail', 'v1', credentials=creds)
	message = MIMEText(body, 'html')
	message['to'] = to
	message['subject'] = subject
	create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
	try:
		message = (service.users().messages().send(userId="me", body=create_message).execute())
		return True
	except HTTPError as error:
		return False


def otp(user, to):
	otp = random.randint(100000, 999999)
	subject = "Your OTP to login at CutYourURL"

	body = f"""Hi {user},
	<br>
	<br>Your OTP to login on CutYourURL is <b>{otp}</b>. Do not share it with anyone!
	<br>
	<br>This OTP is only valid for <a href="https://cutyoururl.pythonanywhere.com/" target="_blank">CutYourURL</a> and is valid for 5 minutes.
	<br>
	<br>Thanks,
	<br>The CutYourURL Team
	<br>
	<br><i>This is an automated email. For help, you can reply to this email and a staff will get in touch very soon.</i>
	<br>
	<br><i>Follow me on my <a href='https://github.com/ashishagarwal2023' target='_blank'>GitHub</a> and give a
	star on the <a href='https://github.com/ashishagarwal2023/CutYourURL' target='_blank'>project</a>!</i>"""

	return email(to, subject, body)

# otp("Ashish", "code.with.aasheesh@gmail.com")

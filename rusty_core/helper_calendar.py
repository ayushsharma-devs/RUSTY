# helper_calendar.py

from __future__ import print_function
import datetime
import os.path
import re
from dateutil import parser as dateparser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/KIIT0001/OneDrive/Desktop/RUSTY/rusty_core/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def parse_reminder(text):
    # Try known structured format first
    match = re.search(r'remind me to (.+?) (\d{1,2})-(\d{1,2})-(\d{2,4}) (\d{1,2}:\d{2})', text, re.IGNORECASE)
    if match:
        task = match.group(1).strip()
        day, month, year = int(match.group(2)), int(match.group(3)), int(match.group(4))
        time_str = match.group(5)
        if year < 100:
            year += 2000
        try:
            dt_obj = datetime.datetime.strptime(f"{year}-{month}-{day} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return None
    else:
        # Try fuzzy parse
        match = re.search(r'remind me to (.+)', text, re.IGNORECASE)
        if not match:
            return None
        task = match.group(1).strip()
        try:
            dt_obj = dateparser.parse(task, fuzzy=True)
            task = re.sub(r'\bat\b.*$', '', task, flags=re.IGNORECASE).strip()  # Remove time part from task
        except Exception:
            return None

    dt_start = dt_obj.isoformat()
    dt_end = (dt_obj + datetime.timedelta(minutes=30)).isoformat()

    return {
        "summary": task,
        "start": dt_start,
        "end": dt_end
    }

def add_event_to_calendar(text):
    data = parse_reminder(text)
    if not data:
        return "🧠 Rusty: I couldn’t understand the reminder format."

    service = authenticate_google_calendar()

    event = {
        'summary': data["summary"],
        'start': {'dateTime': data["start"], 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': data["end"], 'timeZone': 'Asia/Kolkata'},
    }

    service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Reminder '{data['summary']}' added for {data['start']}"

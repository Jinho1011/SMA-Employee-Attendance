from __future__ import print_function
from pytz import timezone, utc
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import datetime
import pickle
import os.path


def check_lunch_time(start, end):
    return True


def get_today_events_from_google_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    if os.path.exists('.config/token-calendar.pickle'):
        with open('.config/token-calendar.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.config/credentials-calendar.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('.config/token-calendar.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    today = datetime.date.today()
    from_ = datetime.datetime(today.year, today.month, today.day, 0, 0, 0,
                              tzinfo=datetime.timezone.utc).isoformat()
    to_ = datetime.datetime(today.year, today.month, today.day, 11, 59, 59,
                            tzinfo=datetime.timezone.utc).isoformat()

    events_result = service.events().list(calendarId='pbinkbigkjdvo9tvb72filfcpo@group.calendar.google.com', timeMin=from_, timeMax=to_,
                                          maxResults=25, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


if __name__ == '__main__':
    events = get_today_events_from_google_calendar()

    staff_txt = open("staffs.txt", 'r')
    staffs_origin = staff_txt.readlines()
    staffs = []

    for staff in staffs_origin:
        staff = staff.strip('\n')
        staffs.append("본 " + staff)
        staffs.append(staff)

    for event in events:
        if event['summary'] in staffs:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            print(start, end, event['summary'])

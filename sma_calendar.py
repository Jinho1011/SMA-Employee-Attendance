from __future__ import print_function
from pytz import timezone, utc
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil.parser import parse
from datetime import datetime, timedelta, date, timezone

import pickle
import os.path

STAFF = []


def get_calendar_service():
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
            creds = flow.run_local_server(port=3030)
        with open('.config/token-calendar.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service.events()


def get_today_events_from_google_calendar(calendar):
    today = date.today()
    from_ = datetime(today.year, today.month, today.day, 0, 0, 0,
                     tzinfo=timezone.utc).isoformat()
    to_ = datetime(today.year, today.month, today.day, 11, 59, 59,
                   tzinfo=timezone.utc).isoformat()

    events_result = calendar.list(calendarId='pbinkbigkjdvo9tvb72filfcpo@group.calendar.google.com', timeMin=from_, timeMax=to_, singleEvents=True,
                                  orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


def get_staff_list():
    STAFF_TXT_FILE = open("staffs.txt", 'r')
    STAFF_LIST_ORIGIN = STAFF_TXT_FILE.readlines()

    STAFF_LIST = []

    for s in STAFF_LIST_ORIGIN:
        s = s.strip('\n').strip()
        STAFF_LIST.append(s)
    return STAFF_LIST


def check_lunch_time(start, end, work_hour, is_head_office):
    if work_hour > 4 and is_head_office:
        if start.hour < 12 and end.hour > 1:
            return True
    else:
        return False


def check_staff_list(summary, list):
    # list 안의 summary에서 (본)과 (스)로 끝나고, list 안에 존재하면 True
    if summary.endswith("(본)"):
        staff_name = summary.split("(본)")[0]
    else:
        staff_name = summary.split("(스)")[0]

    for keyword in list:
        if staff_name == keyword:
            return True

    return None


def main():
    calendar = get_calendar_service()
    events = get_today_events_from_google_calendar(calendar)
    STAFF_LIST = get_staff_list()

    # Implement Today STAFF List
    for event in events:
        event_summary = event["summary"]
        if check_staff_list(event_summary, STAFF_LIST):
            if event_summary.endswith("(본)") or event_summary.endswith("(스)"):
                STAFF_MEMBER = {}

                # staff_name & is_head_office
                if event_summary.endswith("(본)"):
                    STAFF_MEMBER["staff_name"] = event_summary.split("(본)")[0]
                    STAFF_MEMBER["is_head_office"] = True
                elif event_summary.endswith("(스)"):
                    STAFF_MEMBER["staff_name"] = event_summary.split("(스)")[0]
                    STAFF_MEMBER["is_head_office"] = False

                # staff_work_hour
                work_start = parse(event['start']['dateTime'])
                work_end = parse(event['end']['dateTime'])
                work_hour = (work_end-work_start).seconds / 3600
                STAFF_MEMBER["staff_work_hour"] = work_hour

                # is_lunch_included
                STAFF_MEMBER["is_lunch_included"] = check_lunch_time(
                    work_start, work_end, work_hour, STAFF_MEMBER["is_head_office"])

                STAFF.append(STAFF_MEMBER)
            elif event_summary.endswith("휴게"):
                # staff_break_hour
                break_start = parse(event['start']['dateTime'])
                break_end = parse(event['end']['dateTime'])
                break_hour = (break_end-break_start).seconds / 3600
                break_staff_name = staff_name.split("휴게")[0].strip()

                for staff in STAFF:
                    if staff["staff_name"] == staff_name:
                        staff["staff_break_hour"] = break_hour

    # Get Total Work Hour For All Staffs
    for staff in STAFF:
        print(staff)

    return STAFF


if __name__ == '__main__':
    main()

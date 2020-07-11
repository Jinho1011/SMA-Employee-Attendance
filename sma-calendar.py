from __future__ import print_function
from pytz import timezone, utc
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil.parser import parse
from datetime import datetime, timedelta, date, timezone

import pickle
import os.path


def check_staff(staffs, keyword):
    # check keyword is in staffs list
    for staff in staffs:
        if keyword.find(staff) >= 0:
            return True
    return False


def check_lunch_time(start, end, work_hour):
    if work_hour > 4:
        if start.hour < 12 and end.hour > 1:
            return True
    else:
        return False


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

    today = date.today()
    from_ = datetime(today.year, today.month, today.day, 0, 0, 0,
                     tzinfo=timezone.utc).isoformat()
    to_ = datetime(today.year, today.month, today.day, 11, 59, 59,
                   tzinfo=timezone.utc).isoformat()

    # get today's events results
    events_result = service.events().list(calendarId='pbinkbigkjdvo9tvb72filfcpo@group.calendar.google.com', timeMin=from_, timeMax=to_,
                                          maxResults=25, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


if __name__ == '__main__':
    events = get_today_events_from_google_calendar()

    staff_txt = open("staffs.txt", 'r')
    staffs_origin = staff_txt.readlines()  # List

    staffs = []  # List
    staff_manage = []  # List

    for staff in staffs_origin:
        staff = staff.strip('\n').strip()
        staffs.append(staff)

    for event in events:
        if check_staff(staffs, event['summary']):
            if event['summary'].endswith("조교"):
                staff_json = {}

                # 출근, 퇴근 시간
                start = parse(event['start']['dateTime'])
                end = parse(event['end']['dateTime'])

                # 근무 시간
                work_hours = (end-start).seconds / 3600

                # 본사 유무
                if event['summary'].startswith("본"):
                    staff_name = event['summary'][2:]
                else:
                    staff_name = event['summary']

                staff_json["staff_name"] = event['summary']
                staff_json["working_hours"] = work_hours
                staff_json["is_lunch_included"] = check_lunch_time(
                    start, end, work_hours)
                staff_manage.append(staff_json)

            elif event['summary'].endswith("휴게"):
                # 휴게 시작, 종료 시간
                start = parse(event['start']['dateTime'])
                end = parse(event['end']['dateTime'])

                # 근무 시간
                break_hours = (end-start).seconds / 3600

                # 본사 유무
                if event['summary'].startswith("본"):
                    staff_name = event['summary'][2:]
                else:
                    staff_name = event['summary']

                staff_name = staff_name.split("휴게")[0].strip()

                for staff_json in staff_manage:
                    if staff_json["staff_name"] == staff_name:
                        staff_json["break_hours"] = break_hours

    for staff in staff_manage:
        print(staff)

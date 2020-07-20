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
# STAFF = [
#     {
#         "staff_name": "전진호",
#         "staff_work_hour": 7,
#         "staff_break_hour": 0,
#         "is_head_office": True,
#         "is_lunch_included": True
#          최종 근무 시간은 staff_work_hour - staff_break_hour - (0 if is_lunch_included else 1) 이다
#     }
# ]


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


def main():
    calendar = get_calendar_service()
    events = get_today_events_from_google_calendar(calendar)
    STAFF_LIST = get_staff_list()

    for event in events:
        event_summary = event["summary"]
        if event_summary.endswith("(본)") or event_summary.endswith("(스)"):
            STAFF_MEMBER = {}
            # staff_name
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

            print(STAFF_MEMBER)

        elif event_summary.endswith("휴게"):
            pass
            # staff_break_hour

    # for event in events:
    #     if check_staff(staffs, event['summary']):
    #         if event['summary'].endswith("조교"):
    #             staff_json = {}

    #             # 출근, 퇴근 시간
    #             start = parse(event['start']['dateTime'])
    #             end = parse(event['end']['dateTime'])

    #             # 근무 시간
    #             work_hours = (end-start).seconds / 3600

    #             # 본사 유무
    #             if event['summary'].startswith("본"):
    #                 staff_name = event['summary'][2:]
    #             else:
    #                 staff_name = event['summary']

    #             staff_json["staff_name"] = event['summary']
    #             staff_json["working_hours"] = work_hours
    #             staff_json["is_lunch_included"] = check_lunch_time(
    #                 start, end, work_hours, is_bon)
    #             staff_manage.append(staff_json)

    #         elif event['summary'].endswith("휴게"):
    #             # 휴게 시작, 종료 시간
    #             start = parse(event['start']['dateTime'])
    #             end = parse(event['end']['dateTime'])

    #             # 근무 시간
    #             break_hours = (end-start).seconds / 3600

    #             # 본사 유무
    #             if event['summary'].startswith("본"):
    #                 staff_name = event['summary'][2:]
    #             else:
    #                 staff_name = event['summary']

    #             staff_name = staff_name.split("휴게")[0].strip()

    #             for staff_json in staff_manage:
    #                 if staff_json["staff_name"] == staff_name:
    #                     staff_json["break_hours"] = break_hours


if __name__ == '__main__':
    main()

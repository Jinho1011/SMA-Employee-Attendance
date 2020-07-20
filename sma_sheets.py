from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta, date, timezone
import pickle
import os.path
import re
import sma_calendar

TODAY_SHEET = ''
STAFF = sma_calendar.main()


def get_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/drive.file',
              'https://www.googleapis.com/auth/spreadsheets']
    creds = None
    if os.path.exists('.config/token-sheets.pickle'):
        with open('.config/token-sheets.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.config/credentials-sheets.json', SCOPES)
            creds = flow.run_local_server(port=3030)
        with open('.config/token-sheets.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()


def get_wage(sheet, sheet_id):
    SPREADSHEET_RANGE = TODAY_SHEET + '!G2'

    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=SPREADSHEET_RANGE).execute()
    value = result.get('values', [])

    return re.sub("[^0-9]", "", value[0][0][5:])


def get_today_range():
    today = date.today()
    global TODAY_SHEET
    TODAY_SHEET = str(today.year)[
        2:] + '0'+str(today.month) if today.month < 10 else str(today.month)


def write_today_wage(sheet, sheet_id, wage, hour):
    day = date.today().day
    TODAY_RANGE = TODAY_SHEET + '!I' + str(day + 5)
    hourly_wage = format(int(int(wage) * hour), ',')

    body = {
        'values': [
            [hourly_wage]
        ]
    }

    result = sheet.values().update(
        spreadsheetId=sheet_id, range=TODAY_RANGE, body=body, valueInputOption='RAW').execute()


def main():
    sheet = get_sheets_service()
    get_today_range()

    for staff in STAFF:
        if staff["staff_name"] == "전진호 조교":
            print(staff)
            url = staff["staff_sheet_url"]
            wage = get_wage(sheet, url)
            hour = staff["staff_total_work_hour"]
            write_today_wage(sheet, url, wage, hour)


if __name__ == '__main__':
    main()

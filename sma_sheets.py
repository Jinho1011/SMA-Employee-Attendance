from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta, date, timezone
import pickle
import os.path
import re
import sma_calendar
import logging
import logging.handlers

# Record Range Here
RANGE_WAGE = 'C2'
RANGE_MEAL = ''
RAGNE_STATUTORY_LEISURE_PAY = ''
RANGE_POINT = ''

STAFF = sma_calendar.main()
TODAY_SHEET = ''


def write_log(result):
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(message)s')

    fileHandler = logging.FileHandler('./result.log')
    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)

    logger.setLevel(level=logging.DEBUG)
    logger.debug(result)


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


def get_today_range():
    today = date.today()
    global TODAY_SHEET
    TODAY_SHEET = str(today.year)[
        2:] + '0'+str(today.month) if today.month < 10 else str(today.month)


def get_wage(sheet, sheet_id):
    SPREADSHEET_RANGE = TODAY_SHEET + '!' + RANGE_WAGE

    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=SPREADSHEET_RANGE).execute()
    value = result.get('values', [])

    return re.sub("[^0-9]", "", value[0][0][5:])


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
    result["content"] = hourly_wage
    write_log(result)


def write_content(sheet, sheet_id, range, content):
    body = {
        'values': [
            [content]
        ]
    }

    result = sheet.values().update(
        spreadsheetId=sheet_id, range=range, body=body, valueInputOption='RAW').execute()
    result["content"] = content
    write_log(result)


def manage_staff_wage(sheet):
    for staff in STAFF:
        url = staff["staff_sheet_url"]
        wage = get_wage(sheet, url)
        hour = staff["staff_total_work_hour"]

        print(staff["staff_name"], wage, hour)
        # write_today_wage(sheet, url, wage, hour)


def main():
    sheet = get_sheets_service()
    get_today_range()

    # manage_staff_wage(sheet)

    # write point

    # write food expense

    # If you want to insert, use this!
    write_content(
        sheet, '1ZQETW0R8bbfSdH-PELVUCl-4D5KUGQ6wpQkqwdUqcm8', '2007!C4', 'logging')


if __name__ == '__main__':
    main()

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
RAGNE_STATUTORY_LEISURE_PAY = ''

STAFF = sma_calendar.main()
TODAY_SHEET = ''


def write_log(result):
    logg_json = {
        "id": result["spreadsheetId"],
        "range": result["updatedRange"],
        "content": result["content"]
    }
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] >> %(message)s')

    fileHandler = logging.FileHandler('./result.log')
    fileHandler.setFormatter(formatter)

    if (logger.hasHandlers()):
        logger.handlers.clear()

    logger.addHandler(fileHandler)

    logger.setLevel(level=logging.DEBUG)
    logger.debug(logg_json)


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


def write_sheet(sheet, url, wage, hour, is_head, is_lunch_included):
    day = date.today().day
    TODAY_RANGE = TODAY_SHEET + '!D' + str(day + 5)
    hourly_wage = format(int(int(wage) * hour), ',')
    content = ['1,000', '', '', '본' if is_head else '',
               hour, hourly_wage, '식대' if is_lunch_included else '', '', '6,000' if is_lunch_included else '']

    body = {
        'values': [
            content
        ]
    }

    result = sheet.values().update(
        spreadsheetId=url, range=TODAY_RANGE, body=body, valueInputOption='USER_ENTERED').execute()
    result["content"] = content

    write_log(result)


def write_today_wage(sheet, sheet_id, wage, hour, is_head):
    day = date.today().day
    TODAY_RANGE = TODAY_SHEET + '!G' + str(day + 5)
    hourly_wage = format(int(int(wage) * hour), ',')
    wage_content = ['본' if is_head else '', hour, hourly_wage]

    body = {
        'values': [
            content
        ]
    }

    result = sheet.values().update(
        spreadsheetId=sheet_id, range=TODAY_RANGE, body=body, valueInputOption='USER_ENTERED').execute()
    result["content"] = content

    write_log(result)


def write_point(sheet, sheet_id):
    day = date.today().day
    TODAY_RANGE = TODAY_SHEET + '!D' + str(day + 5)
    point = '1,000'

    body = {
        'values': [
            [point]
        ]
    }

    result = sheet.values().update(
        spreadsheetId=sheet_id, range=TODAY_RANGE, body=body, valueInputOption='RAW').execute()
    result["content"] = point
    write_log(result)


def write_food_expense(sheet, sheet_id):
    day = date.today().day
    TODAY_RANGE = TODAY_SHEET + '!J' + str(day + 5)
    food_expense = '6,000'

    body = {
        'values': [
            ['식대', '', food_expense]
        ]
    }

    result = sheet.values().update(
        spreadsheetId=sheet_id, range=TODAY_RANGE, body=body, valueInputOption='RAW').execute()
    result["content"] = food_expense
    write_log(result)


def write_content(sheet, sheet_id, range, content):
    body = {
        'values': [
            content
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
        is_head = staff["is_head_office"]

        write_today_wage(sheet, url, wage, hour, is_head)


def manage_staff_point(sheet):
    for staff in STAFF:
        url = staff["staff_sheet_url"]
        write_point(sheet, url)


def manage_staff_food_expense(sheet):
    for staff in STAFF:
        url = staff["staff_sheet_url"]
        write_food_expense(sheet, url)


def manage_all(sheet):
    for staff in STAFF:
        print(staff)
        url = staff["staff_sheet_url"]
        wage = get_wage(sheet, url)
        hour = staff["staff_total_work_hour"]
        is_head = staff["is_head_office"]
        is_lunch_included = staff["is_lunch_included"]
        write_sheet(sheet, url, wage, hour, is_head, is_lunch_included)


def main():
    sheet = get_sheets_service()
    get_today_range()

    # manage_staff_wage(sheet)

    # manage_staff_point(sheet)

    # manage_staff_food_expense(sheet)

    manage_all(sheet)

    # If you want to insert, use this!
    # write_content(
    #     sheet, '1ZQETW0R8bbfSdH-PELVUCl-4D5KUGQ6wpQkqwdUqcm8', '2007!I29', [''])


if __name__ == '__main__':
    main()

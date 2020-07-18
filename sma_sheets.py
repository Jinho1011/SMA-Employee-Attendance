from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta, date, timezone
import pickle
import os.path
import re
import sma_calendar


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
    SPREADSHEET_RANGE = '2007!C2'
    SPREADSHEET_ID = sheet_id

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=SPREADSHEET_RANGE).execute()
    value = result.get('values', [])

    return re.sub("[^0-9]", "", value[0][0][8:])


if __name__ == '__main__':
    sheet = get_sheets_service()

    wage = get_wage(sheet, '1ZQETW0R8bbfSdH-PELVUCl-4D5KUGQ6wpQkqwdUqcm8')

    # SPREADSHEET_RANGE = '2007!I21'
    # body = {
    #     'values': [
    #         [""]
    #     ]
    # }
    # result = sheet.values().update(
    #     spreadsheetId=SPREADSHEET_ID, range=SPREADSHEET_RANGE, body=body, valueInputOption='RAW').execute()
